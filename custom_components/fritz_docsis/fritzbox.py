import hashlib
            timeout=10,
        )

        challenge = re.search(
            r"<Challenge>(.*?)</Challenge>",
            response.text,
        ).group(1)

        challenge_response = challenge + "-" + hashlib.md5(
            (challenge + "-" + self.password).encode("utf-16le")
        ).hexdigest()

        sid_response = requests.get(
            f"http://{self.host}/login_sid.lua",
            params={
                "username": self.username,
                "response": challenge_response,
            },
            timeout=10,
        )

        sid = re.search(
            r"<SID>(.*?)</SID>",
            sid_response.text,
        ).group(1)

        return sid

    def get_docsis_data(self):

        sid = self._get_sid()

        response = requests.get(
            f"http://{self.host}/internet/inetstat_monitor.lua",
            params={"sid": sid},
            timeout=10,
        )

        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")

        if len(tables) < 2:
            raise Exception("DOCSIS Tabellen nicht gefunden")

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

            data["docsis31"] = {
                "power": float(cols[3].text.strip().replace(",", ".")),
                "mer": float(cols[4].text.strip().replace(",", ".")),
                "uncorrectable": int(cols[7].text.strip()),
            }

        for row in docsis30_rows[1:]:

            cols = row.find_all("td")

            if len(cols) < 8:
                continue

            try:
                data["docsis30"].append(
                    {
                        "channel": cols[0].text.strip(),
                        "power": float(cols[3].text.strip().replace(",", ".")),
                        "mse": float(cols[4].text.strip().replace(",", ".")),
                        "latency": float(cols[5].text.strip().replace(",", ".")),
                        "correctable": int(cols[6].text.strip()),
                        "uncorrectable": int(cols[7].text.strip()),
                    }
                )
            except Exception:
                pass

        return data
