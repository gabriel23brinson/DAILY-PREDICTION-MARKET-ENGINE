from engine.scan_today import run_today

if __name__=="__main__":
    r=run_today(persist=True)
    print(f"same_day={r.same_day} supported={r.supported} paper={r.paper} passed={r.passed} failed={r.failed} resolved={r.newly_resolved}")
