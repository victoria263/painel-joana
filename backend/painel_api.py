#!/usr/bin/env python3
"""API do Painel de Monitoramento da Joana (ADERE.AI).

Alimenta o painel EM TEMPO REAL a partir dos dados que a própria Joana escreve:
- conversas: data/conversations/whatsapp/<telefone>.md (a Joana grava ao vivo)
- fatos clínicos (marcos + ciclos): data/painel/clinico.json (a Joana mantém)

Endpoints:
- GET /api/patients            -> lista de pacientes (modelo do painel)
- GET /api/patients/{telefone} -> uma paciente
- GET /api/stream              -> Server-Sent Events, empurra quando algo muda
- GET /health

Só PACIENTES aparecem (a Dra. Isabelle, a Victoria e a secretaria do Instituto Donna ficam de fora).
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

BASE = Path("/home/assistente/adereai")
CONV = BASE / "data/conversations/whatsapp"
CLINICO = BASE / "data/painel/clinico.json"
STATIC = Path(__file__).resolve().parent / "static"

# Só pacientes (telefone -> nome de fallback). A fonte de nome é o clinico.json.
PACIENTES = {
    "5511983929279": "Renata Lovetro",
    "5511999100016": "Anna Paola",
    "5511976919161": "Patrícia Guimarães",
    "5511974421122": "Thaís Thomazzoni",
}

LINE_RE = re.compile(r"^\[(?P<ts>[^\]]+)\]\s*(?P<quem>paciente|Joana)\s*:\s*(?P<txt>.*)$")

app = FastAPI(title="Painel Joana API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


def _parse_conversa(telefone: str) -> tuple[list[dict], bool, str | None]:
    """Lê o .md da conversa -> (mensagens, ativa, ultimaInteracao_iso)."""
    f = CONV / f"{telefone}.md"
    if not f.exists():
        return [], False, None
    msgs: list[dict] = []
    cur: dict | None = None
    for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = LINE_RE.match(line)
        if m:
            if cur:
                msgs.append(cur)
            de = "paciente" if m.group("quem") == "paciente" else "joana"
            cur = {"de": de, "texto": m.group("txt"), "ts": m.group("ts")}
        elif cur is not None:
            cur["texto"] += "\n" + line
    if cur:
        msgs.append(cur)

    ativa = any(x["de"] == "paciente" for x in msgs)
    ultima = msgs[-1]["ts"] if msgs else None
    # formata hora curta pra cada msg
    for x in msgs:
        try:
            dt = datetime.fromisoformat(x["ts"])
            x["hora"] = dt.astimezone().strftime("%d/%m %H:%M")
        except Exception:
            x["hora"] = x["ts"][:16]
    return msgs, ativa, ultima


def _load_clinico() -> dict:
    try:
        return json.loads(CLINICO.read_text(encoding="utf-8")).get("pacientes", {})
    except Exception:
        return {}


def _paciente(telefone: str, clinico: dict) -> dict:
    msgs, ativa, ultima = _parse_conversa(telefone)
    c = clinico.get(telefone, {})
    return {
        "telefone": telefone,
        "nome": c.get("nome") or PACIENTES.get(telefone, telefone),
        "foto": c.get("foto"),
        "ativa": ativa,
        "ultimaInteracao": ultima,
        "mensagens": msgs,
        "marcos": c.get("marcos", {}),
        "ciclos": c.get("ciclos", []),
    }


def _todos() -> list[dict]:
    clinico = _load_clinico()
    return [_paciente(t, clinico) for t in PACIENTES]


def _fingerprint() -> str:
    """Assinatura barata do estado (mtime dos arquivos) pra detectar mudança."""
    parts = []
    for t in PACIENTES:
        f = CONV / f"{t}.md"
        parts.append(str(f.stat().st_mtime) if f.exists() else "0")
    parts.append(str(CLINICO.stat().st_mtime) if CLINICO.exists() else "0")
    return "|".join(parts)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"ok": True, "pacientes": len(PACIENTES), "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/api/patients")
def patients():
    todos = _todos()
    return {
        "total": len(todos),
        "ativas": sum(1 for p in todos if p["ativa"]),
        "pacientes": todos,
    }


@app.get("/api/patients/{telefone}")
def patient(telefone: str):
    if telefone not in PACIENTES:
        raise HTTPException(404, "paciente não encontrada")
    return _paciente(telefone, _load_clinico())


@app.get("/api/stream")
async def stream():
    async def gen():
        last = None
        # manda o estado inicial na hora
        while True:
            fp = _fingerprint()
            if fp != last:
                last = fp
                payload = json.dumps(patients())
                yield f"event: update\ndata: {payload}\n\n"
            else:
                yield ": keepalive\n\n"
            await asyncio.sleep(3)
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
