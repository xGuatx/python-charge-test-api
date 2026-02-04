import subprocess
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

data = {"url": "https://google.com", "delay": 1}

EXPECTED_KEYS = {"request_id", "screenshot", "session_id"}


def send_curl_request():
    t0 = time.time()
    cmd = [
        "curl",
        "-k",
        "-s",
        "-w",
        "HTTPSTATUS:%{http_code}|TOTALTIME:%{time_total}",
        "-X",
        "POST",
        "https://192.168.164.5/capture_screenshot",
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(data),
    ]
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90
        )
        elapsed = time.time() - t0
        output = result.stdout
        # On extrait les infos ajoutees a la fin
        if "HTTPSTATUS:" in output and "TOTALTIME:" in output:
            split1 = output.rsplit("HTTPSTATUS:", 1)
            body = split1[0]
            status_time = split1[1]
            status_part = status_time.split("|TOTALTIME:")
            http_code = status_part[0].strip()
            total_time = float(status_part[1].strip())
        else:
            body = output
            http_code = "???"
            total_time = elapsed

        # On verifie le retour
        try:
            js = json.loads(body)
            keys = set(js)
            missing = EXPECTED_KEYS - keys
            empty = [k for k in EXPECTED_KEYS if not js.get(k)]
            if missing or empty or http_code != "200":
                return {
                    "success": False,
                    "http_code": http_code,
                    "total_time": total_time,
                    "error": f"missing: {missing} empty: {empty}",
                    "raw": body.strip()[:100],
                }
            return {"success": True, "http_code": http_code, "total_time": total_time}
        except Exception as e:
            return {
                "success": False,
                "http_code": http_code,
                "total_time": total_time,
                "error": f"JSON error: {e}",
                "raw": body.strip()[:100],
            }
    except Exception as e:
        return {
            "success": False,
            "http_code": "???",
            "total_time": None,
            "error": f"Exception Python: {e}",
            "raw": "",
        }


# Parametres de la campagne de test
steps = [2, 4, 8, 16, 32, 64]  # nombre de requetes simultanees a chaque etape
sleep_between_steps = 5  # secondes a attendre entre les etapes

for num_parallel in steps:
    print(f"\n=== Test avec {num_parallel} requetes paralleles ===")
    results = []
    t_step0 = time.time()
    with ThreadPoolExecutor(max_workers=num_parallel) as executor:
        futures = [executor.submit(send_curl_request) for _ in range(num_parallel)]
        for i, future in enumerate(as_completed(futures), 1):
            res = future.result()
            results.append(res)
            status = "OK" if res["success"] else "FAIL"
            print(
                f"{i:02d}: [{status}] code={res['http_code']} t={res['total_time']:.2f}s",
                end="",
            )
            if not res["success"]:
                print(f" | err={res.get('error','')}")
            else:
                print()

    # Resume pour cette etape
    total_times = [r["total_time"] for r in results if r["total_time"] is not None]
    err_count = sum(1 for r in results if not r["success"])
    print(f"\nResume pour {num_parallel} requetes :")
    print(f"  Temps min    : {min(total_times):.2f}s")
    print(f"  Temps max    : {max(total_times):.2f}s")
    print(f"  Temps moyen  : {mean(total_times):.2f}s")
    print(f"  Erreurs      : {err_count}/{num_parallel}")
    print(f"  Taux erreur  : {err_count/num_parallel*100:.1f}%")
    if err_count:
        print("  -> Details premieres erreurs :")
        for r in results:
            if not r["success"]:
                print("    -", r["error"], "| raw:", r.get("raw", ""))
    t_step1 = time.time()
    print(f"  Duree totale pour l'etape : {t_step1-t_step0:.2f}s")
    print("=" * 60)
    time.sleep(sleep_between_steps)

