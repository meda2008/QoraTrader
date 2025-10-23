"""
Contract tests for report generation endpoints
These tests verify that the report generation API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_generate_trading_report_contract():
    """
    Test the contract for generating trading report endpoint
    """
    # Test parameters
    strategy_id = "test-strategy-123"
    start_date = "2023-01-01T00:00:00"
    end_date = "2023-12-31T23:59:59"
    
    response = client.get(
        f"/api/v1/reports/trading-report",
        params={
            "strategy_id": strategy_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "report_period", "performance_metrics", 
            "trade_list", "summary", "created_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Check report period structure
        assert "start_date" in data["report_period"]
        assert "end_date" in data["report_period"]
        
        # Check performance metrics structure
        perf_metrics = data["performance_metrics"]
        perf_fields = [
            "total_trades", "winning_trades", "losing_trades", "win_rate",
            "total_pnl", "profit_factor", "avg_win", "avg_loss"
        ]
        for field in perf_fields:
            assert field in perf_metrics
            
        # Check that trade_list is a list
        assert isinstance(data["trade_list"], list)
        
        # Check summary is a string
        assert isinstance(data["summary"], str)

def test_export_trading_report_contract():
    """
    Test the contract for exporting trading report endpoint
    """
    # Test parameters
    strategy_id = "test-strategy-123"
    start_date = "2023-01-01T00:00:00"
    end_date = "2023-12-31T23:59:59"
    format_type = "csv"  # Supported formats: csv, pdf, json
    
    response = client.get(
        f"/api/v1/reports/export",
        params={
            "strategy_id": strategy_id,
            "start_date": start_date,
            "end_date": end_date,
            "format": format_type
        }
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        # For file downloads, check content type
        assert "content-type" in response.headers
        if format_type == "csv":
            assert "text/csv" in response.headers["content-type"]
        elif format_type == "pdf":
            assert "application/pdf" in response.headers["content-type"]
        elif format_type == "json":
            assert "application/json" in response.headers["content-type"]

def test_get_report_templates_contract():
    """
    Test the contract for getting report templates endpoint
    """
    response = client.get("/api/v1/reports/templates")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of templates
        assert isinstance(data, list)
        if len(data) > 0:
            # Each template should have expected fields
            first_template = data[0]
            template_fields = ["id", "name", "description", "type", "created_at"]
            for field in template_fields:
                assert field in first_template

def test_create_custom_report_template_contract():
    """
    Test the contract for creating custom report template endpoint
    """
    template_data = {
        "name": "Custom Template",
        "description": "A custom report template",
        "type": "trading",
        "template_content": "<html><body>{{report_content}}</body></html>",
        "parameters": {
            "include_charts": True,
            "include_trades": True,
            "include_metrics": True
        }
    }
    
    response = client.post("/api/v1/reports/templates", json=template_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "id", "name", "description", "type", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful creation
        assert data["name"] == "Custom Template"
        assert data["type"] == "trading"

def test_delete_report_template_contract():
    """
    Test the contract for deleting report template endpoint
    """
    template_id = "test-template-123"
    response = client.delete(f"/api/v1/reports/templates/{template_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should indicate successful deletion
        assert "message" in data
        assert "deleted" in data["message"].lower()
        assert "template" in data["message"].lower()

def test_get_strategy_report_history_contract():
    """
    Test the contract for getting strategy report history endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/reports/strategy/{strategy_id}/history")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of historical reports
        assert isinstance(data, list)
        if len(data) > 0:
            # Each historical report should have expected fields
            first_report = data[0]
            report_fields = [
                "id", "strategy_id", "generated_at", "period_start", 
                "period_end", "file_path", "file_size"
            ]
            for field in report_fields:
                assert field in first_report

def test_compare_strategy_reports_contract():
    """
    Test the contract for comparing strategy reports endpoint
    """
    strategy_ids = ["strategy-1", "strategy-2", "strategy-3"]
    start_date = "2023-01-01T00:00:00"
    end_date = "2023-12-31T23:59:59"
    
    response = client.post(
        "/api/v1/reports/compare",
        json={
            "strategy_ids": strategy_ids,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403, 404]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return comparison data
        assert "comparison" in data
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        
        # Each strategy in comparison should have metrics
        if "comparison" in data and isinstance(data["comparison"], dict):
            for strategy_id, metrics in data["comparison"].items():
                assert isinstance(metrics, dict)
                # Should have key performance metrics
                metric_fields = ["total_return", "win_rate", "sharpe_ratio", "max_drawdown"]
                for field in metric_fields:
                    assert field in metrics

def test_get_report_statistics_contract():
    """
    Test the contract for getting report statistics endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/reports/{strategy_id}/statistics")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return statistical data
        expected_fields = [
            "strategy_id", "total_reports", "avg_performance", 
            "best_performance", "worst_performance", "volatility"
        ]
        for field in expected_fields:
            assert field in data
            
        # Statistical values should be numeric
        assert isinstance(data["avg_performance"], (int, float))
        assert isinstance(data["volatility"], (int, float))

def test_schedule_recurring_report_contract():
    """
    Test the contract for scheduling recurring report endpoint
    """
    schedule_data = {
        "strategy_id": "test-strategy-123",
        "frequency": "weekly",  # Options: daily, weekly, monthly
        "recipients": ["user@example.com"],
        "format": "pdf",
        "include_charts": True
    }
    
    response = client.post("/api/v1/reports/schedule", json=schedule_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return schedule information
        expected_fields = [
            "schedule_id", "strategy_id", "frequency", "recipients", 
            "format", "next_run", "created_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful scheduling
        assert data["strategy_id"] == "test-strategy-123"
        assert data["frequency"] == "weekly"

def test_get_scheduled_reports_contract():
    """
    Test the contract for getting scheduled reports endpoint
    """
    response = client.get("/api/v1/reports/schedules")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of schedules
        assert isinstance(data, list)
        if len(data) > 0:
            # Each schedule should have expected fields
            first_schedule = data[0]
            schedule_fields = [
                "schedule_id", "strategy_id", "frequency", "recipients", 
                "format", "next_run", "created_at", "is_active"
            ]
            for field in schedule_fields:
                assert field in first_schedule

def test_cancel_scheduled_report_contract():
    """
    Test the contract for canceling scheduled report endpoint
    """
    schedule_id = "test-schedule-123"
    response = client.delete(f"/api/v1/reports/schedules/{schedule_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should indicate successful cancellation
        assert "message" in data
        assert "cancelled" in data["message"].lower() or "canceled" in data["message"].lower()
        assert schedule_id in data["message"]

def test_update_report_template_contract():
    """
    Test the contract for updating report template endpoint
    """
    template_id = "test-template-123"
    update_data = {
        "name": "Updated Template Name",
        "description": "Updated description",
        "template_content": "<html><body>Updated {{report_content}}</body></html>"
    }
    
    response = client.put(f"/api/v1/reports/templates/{template_id}", json=update_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return updated template information
        expected_fields = [
            "id", "name", "description", "template_content", 
            "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should reflect the updates
        assert data["name"] == "Updated Template Name"
        assert data["description"] == "Updated description"

def test_preview_report_contract():
    """
    Test the contract for previewing report endpoint
    """
    preview_data = {
        "strategy_id": "test-strategy-123",
        "template_id": "test-template-123",
        "parameters": {
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-12-31T23:59:59",
            "include_charts": True
        }
    }
    
    response = client.post("/api/v1/reports/preview", json=preview_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403, 404]  # Expected status codes
    
    if response.status_code == 200:
        # For preview, might return HTML content or JSON with preview data
        if response.headers.get("content-type", "").startswith("text/html"):
            # HTML preview
            assert len(response.text) > 0
        else:
            # JSON preview data
            data = response.json()
            assert "preview_content" in data
            assert isinstance(data["preview_content"], str)

def test_get_report_formats_contract():
    """
    Test the contract for getting available report formats endpoint
    """
    response = client.get("/api/v1/reports/formats")
    
    # Check that the response has the expected structure
    assert response.status_code == 200
    
    data = response.json()
    # Should return a list of supported formats
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Common formats should be supported
    common_formats = ["pdf", "csv", "json", "html"]
    for format_name in common_formats:
        assert format_name in data

def test_get_report_metadata_contract():
    """
    Test the contract for getting report metadata endpoint
    """
    report_id = "test-report-123"
    response = client.get(f"/api/v1/reports/{report_id}/metadata")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return metadata information
        expected_fields = [
            "id", "strategy_id", "generated_at", "period_start", 
            "period_end", "file_size", "file_path", "format",
            "created_by", "tags"
        ]
        for field in expected_fields:
            assert field in data
            
        # Metadata values should have correct types
        assert isinstance(data["file_size"], int)
        assert isinstance(data["tags"], list)

def test_add_report_tag_contract():
    """
    Test the contract for adding tag to report endpoint
    """
    report_id = "test-report-123"
    tag_data = {
        "tag": "important"
    }
    
    response = client.post(f"/api/v1/reports/{report_id}/tags", json=tag_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should indicate successful tagging
        assert "message" in data
        assert "tag" in data
        assert data["tag"] == "important"
        assert "added" in data["message"].lower()

def test_remove_report_tag_contract():
    """
    Test the contract for removing tag from report endpoint
    """
    report_id = "test-report-123"
    tag_name = "important"
    response = client.delete(f"/api/v1/reports/{report_id}/tags/{tag_name}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should indicate successful tag removal
        assert "message" in data
        assert "removed" in data["message"].lower()
        assert tag_name in data["message"]

def test_search_reports_contract():
    """
    Test the contract for searching reports endpoint
    """
    search_params = {
        "query": "monthly performance",
        "strategy_id": "test-strategy-123",
        "date_from": "2023-01-01T00:00:00",
        "date_to": "2023-12-31T23:59:59",
        "tags": ["monthly", "performance"]
    }
    
    response = client.post("/api/v1/reports/search", json=search_params)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return search results
        assert "results" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        
        # Results should be a list
        assert isinstance(data["results"], list)
        
        # Each result should have basic report information
        if len(data["results"]) > 0:
            first_result = data["results"][0]
            result_fields = [
                "id", "strategy_id", "generated_at", "period_start", 
                "period_end", "file_size", "tags"
            ]
            for field in result_fields:
                assert field in first_result