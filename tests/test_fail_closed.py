from src.run_daily import main


def test_job_fails_closed_until_real_data_pipeline_exists():
    assert main() != 0
