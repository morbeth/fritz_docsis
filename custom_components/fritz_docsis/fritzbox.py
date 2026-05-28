import hashlib
import re

import requests
from bs4 import BeautifulSoup

# DOCSIS-Seitenpfade, die nacheinander versucht werden
DOCSIS_PATHS = [
    "/docsis_info.lua",
    "/cable/docsis_info.lua",
]


class FritzDocsis:

    def __init__(
        self,
        host,
        username,
        password,
    ):

        self.host = host
        self.username = username
        self.password = password

    def _get_sid(self):
        """
        Login mit MD5-Challenge (FritzOS < 7.24 kompatibel).
        Falls die SID ungültig zurückkommt (lauter Nullen),
        wird eine Exception geworfen.
        """

        response = requests.get(
            f"http://{self.host}/login_sid.lua",
            params={"version": "2"},
            timeout=10,
        )

        challenge = re.search(
            r"<Challenge>(.*?)</Challenge>",
            response.text,
        ).group(1)

        # Ab FritzOS 7.24: Challenge beginnt mit "2$" → pbkdf2
        if challenge.startswith("2$"):
            sid = self._get_sid_pbkdf2(challenge)
        else:
            sid = self._get_sid_md5(challenge)

        if sid == "0000000000000000":
            raise Exception(
                "FritzBox Login fehlgeschlagen – "
                "Benutzername oder Passwort falsch."
            )

        return sid

    def _get_sid_md5(self, challenge):
        """Altes MD5-Verfahren (FritzOS < 7.24)."""

        challenge_response = (
            challenge
            + "-"
            + hashlib.md5(
                (challenge + "-" + self.password).encode("utf-16le")
            ).hexdigest()
        )

        response = requests.get(
            f"http://{self.host}/login_sid.lua",
            params={
                "username": self.username,
                "response": challenge_response,
            },
            timeout=10,
        )

        return re.search(
            r"<SID>(.*?)</SID>",
            response.text,
        ).group(1)

    def _get_sid_pbkdf2(self, challenge):
        """
        Neues pbkdf2-Verfahren ab FritzOS 7.24.
        Challenge-Format: 2$<iter1>$<salt1>$<iter2>$<salt2>
        """

        # Format: 2$<iter1>$<salt1>$<iter2>$<salt2>
        parts = challenge.split("$")
        # parts[0] = "2"
        iter1  = int(parts[1])
        salt1  = bytes.fromhex(parts[2])
        iter2  = int(parts[3])
        salt2  = bytes.fromhex(parts[4])

        hash1 = hashlib.pbkdf2_hmac(
            "sha256",
            self.password.encode("utf-8"),
            salt1,
            iter1,
        )

        hash2 = hashlib.pbkdf2_hmac(
            "sha256",
            hash1,
            salt2,
            iter2,
        )

        challenge_response = f"2${parts[2]}${hash2.hex()}"

        response = requests.get(
            f"http://{self.host}/login_sid.lua",
            params={
                "username": self.username,
                "response": challenge_response,
            },
            timeout=10,
        )

        return re.search(
            r"<SID>(.*?)</SID>",
            response.text,
        ).group(1)

    def _fetch_docsis_page(self, sid):
        """
        Versucht nacheinander bekannte DOCSIS-Pfade.
        Gibt (soup, pfad) zurück sobald Tabellen gefunden werden.
        """

        for path in DOCSIS_PATHS:
            response = requests.get(
                f"http://{self.host}{path}",
                params={"sid": sid},
                timeout=10,
            )

            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            if len(tables) >= 2:
                return soup, path

        raise Exception(
            "DOCSIS Tabellen nicht gefunden. "
            "Überprüfe ob deine FritzBox ein Kabel-Modell ist "
            f"und ob eine der folgenden URLs erreichbar ist: "
            f"{', '.join(DOCSIS_PATHS)}"
        )

    def get_docsis_data(self):

        sid = self._get_sid()
        soup, _ = self._fetch_docsis_page(sid)

        tables = soup.find_all("table")

        docsis31_table = tables[0]
        docsis30_table = tables[1]

        docsis31_rows = docsis31_table.find_all("tr")
        docsis30_rows = docsis30_table.find_all("tr")

        data = {
            "docsis31": {},
            "docsis30": [],
        }

        if len(docsis31_rows) > 1:

            cols = docsis31_rows[1].find_all("td")

            if len(cols) >= 8:
                data["docsis31"] = {
                    "power": _parse_float(cols[3].text),
                    "mer":   _parse_float(cols[4].text),
                    "uncorrectable": _parse_int(cols[7].text),
                }

        for row in docsis30_rows[1:]:

            cols = row.find_all("td")

            if len(cols) < 8:
                continue

            try:
                data["docsis30"].append(
                    {
                        "channel":       cols[0].text.strip(),
                        "power":         _parse_float(cols[3].text),
                        "mse":           _parse_float(cols[4].text),
                        "latency":       _parse_float(cols[5].text),
                        "correctable":   _parse_int(cols[6].text),
                        "uncorrectable": _parse_int(cols[7].text),
                    }
                )
            except Exception:
                pass

        return data


# --- Hilfsfunktionen ---

def _parse_float(text: str) -> float:
    """Bereinigt Einheiten wie 'dBmV', 'dB' und wandelt Komma→Punkt um."""
    clean = re.sub(r"[^\d,.\-]", "", text.strip()).replace(",", ".")
    return float(clean)


def _parse_int(text: str) -> int:
    clean = re.sub(r"[^\d]", "", text.strip())
    return int(clean) if clean else 0
