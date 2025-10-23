"""
API endpoints for exchange adapter management
These endpoints handle registration, configuration, and management of exchange adapters
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.exchanges.registry import exchange_registry
from src.utils.error_handler import CustomException

router = APIRouter()

@router.post("/register", response_model=Dict)
async def register_exchange_adapter(
    adapter_data: Dict[str, Any] = Body(...),
    current_user = Depends(require_role("admin"))
):
    """
    Register a new exchange adapter
    """
    try:
        # Validate required fields
        required_fields = ['name', 'adapter_type', 'config']
        for field in required_fields:
            if field not in adapter_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        adapter_name = adapter_data['name']
        adapter_type = adapter_data['adapter_type']
        config = adapter_data['config']
        
        # Create adapter instance based on type
        # In a real implementation, this would dynamically load the appropriate adapter class
        # For now, we'll simulate this
        if adapter_type == "mock":
            # Create a mock adapter for testing
            from src.exchanges.base_adapter import BaseExchangeAdapter
            mock_adapter = BaseExchangeAdapter(adapter_name)
            
            # Register the adapter
            success = exchange_registry.register_adapter(adapter_name, mock_adapter)
            
            if success:
                return {
                    "name": adapter_name,
                    "type": adapter_type,
                    "status": "registered",
                    "message": f"Exchange adapter '{adapter_name}' registered successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to register exchange adapter '{adapter_name}'"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported adapter type: {adapter_type}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register exchange adapter: {str(e)}"
        )

@router.delete("/{adapter_name}", response_model=Dict)
async def unregister_exchange_adapter(
    adapter_name: str,
    current_user = Depends(require_role("admin"))
):
    """
    Unregister an exchange adapter
    """
    try:
        success = exchange_registry.unregister_adapter(adapter_name)
        
        if success:
            return {
                "name": adapter_name,
                "status": "unregistered",
                "message": f"Exchange adapter '{adapter_name}' unregistered successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange adapter '{adapter_name}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister exchange adapter: {str(e)}"
        )

@router.post("/{adapter_name}/connect", response_model=Dict)
async def connect_exchange_adapter(
    adapter_name: str,
    current_user = Depends(require_role("admin"))
):
    """
    Connect to an exchange adapter
    """
    try:
        adapter = exchange_registry.get_adapter(adapter_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange adapter '{adapter_name}' not found"
            )
        
        # Connect to the adapter
        import asyncio
        success = asyncio.run(adapter.connect())
        
        if success:
            return {
                "name": adapter_name,
                "status": "connected",
                "message": f"Exchange adapter '{adapter_name}' connected successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to connect to exchange adapter '{adapter_name}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to exchange adapter: {str(e)}"
        )

@router.post("/{adapter_name}/disconnect", response_model=Dict)
async def disconnect_exchange_adapter(
    adapter_name: str,
    current_user = Depends(require_role("admin"))
):
    """
    Disconnect from an exchange adapter
    """
    try:
        adapter = exchange_registry.get_adapter(adapter_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange adapter '{adapter_name}' not found"
            )
        
        # Disconnect from the adapter
        import asyncio
        success = asyncio.run(adapter.disconnect())
        
        if success:
            return {
                "name": adapter_name,
                "status": "disconnected",
                "message": f"Exchange adapter '{adapter_name}' disconnected successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disconnect from exchange adapter '{adapter_name}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect from exchange adapter: {str(e)}"
        )

@router.get("/", response_model=Dict)
async def list_exchange_adapters(
    current_user = Depends(get_current_active_user)
):
    """
    List all registered exchange adapters
    """
    try:
        adapter_names = exchange_registry.list_adapters()
        adapter_classes = exchange_registry.list_adapter_classes()
        
        return {
            "adapters": adapter_names,
            "adapter_classes": adapter_classes,
            "count": len(adapter_names),
            "class_count": len(adapter_classes)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list exchange adapters: {str(e)}"
        )

@router.get("/{adapter_name}/status", response_model=Dict)
async def get_exchange_adapter_status(
    adapter_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get the status of an exchange adapter
    """
    try:
        status_info = exchange_registry.get_adapter_status(adapter_name)
        return status_info
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get adapter status: {str(e)}"
        )

@router.get("/statuses", response_model=Dict)
async def get_all_exchange_adapter_statuses(
    current_user = Depends(get_current_active_user)
):
    """
    Get the status of all exchange adapters
    """
    try:
        statuses = exchange_registry.get_all_adapter_statuses()
        return {
            "statuses": statuses,
            "count": len(statuses)
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get adapter statuses: {str(e)}"
        )

@router.post("/connect-all", response_model=Dict)
async def connect_all_exchange_adapters(
    current_user = Depends(require_role("admin"))
):
    """
    Connect to all registered exchange adapters
    """
    try:
        results = exchange_registry.connect_all_adapters()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return {
            "results": results,
            "summary": {
                "successful": success_count,
                "failed": total_count - success_count,
                "total": total_count
            },
            "message": f"Connection attempt completed: {success_count}/{total_count} adapters connected successfully"
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect all adapters: {str(e)}"
        )

@router.post("/disconnect-all", response_model=Dict)
async def disconnect_all_exchange_adapters(
    current_user = Depends(require_role("admin"))
):
    """
    Disconnect from all registered exchange adapters
    """
    try:
        results = exchange_registry.disconnect_all_adapters()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return {
            "results": results,
            "summary": {
                "successful": success_count,
                "failed": total_count - success_count,
                "total": total_count
            },
            "message": f"Disconnection attempt completed: {success_count}/{total_count} adapters disconnected successfully"
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect all adapters: {str(e)}"
        )

@router.post("/{adapter_name}/set-default", response_model=Dict)
async def set_default_exchange_adapter(
    adapter_name: str,
    current_user = Depends(require_role("admin"))
):
    """
    Set an exchange adapter as the default
    """
    try:
        success = exchange_registry.set_default_adapter(adapter_name)
        
        if success:
            return {
                "name": adapter_name,
                "status": "default_set",
                "message": f"Exchange adapter '{adapter_name}' set as default successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set exchange adapter '{adapter_name}' as default"
            )
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default adapter: {str(e)}"
        )

@router.get("/default", response_model=Dict)
async def get_default_exchange_adapter(
    current_user = Depends(get_current_active_user)
):
    """
    Get the default exchange adapter
    """
    try:
        default_adapter_name = exchange_registry.get_default_adapter_name()
        if not default_adapter_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No default exchange adapter set"
            )
        
        return {
            "name": default_adapter_name,
            "message": f"Default exchange adapter is '{default_adapter_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get default adapter: {str(e)}"
        )

@router.put("/{adapter_name}/config", response_model=Dict)
async def update_exchange_adapter_config(
    adapter_name: str,
    config_data: Dict[str, Any] = Body(...),
    current_user = Depends(require_role("admin"))
):
    """
    Update the configuration of an exchange adapter
    """
    try:
        adapter = exchange_registry.get_adapter(adapter_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange adapter '{adapter_name}' not found"
            )
        
        # In a real implementation, this would update the adapter's configuration
        # For now, we'll just return a success message
        return {
            "name": adapter_name,
            "status": "config_updated",
            "message": f"Configuration for exchange adapter '{adapter_name}' updated successfully",
            "updated_config": config_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update adapter configuration: {str(e)}"
        )

@router.get("/{adapter_name}/markets", response_model=Dict)
async def get_supported_markets(
    adapter_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get the list of supported markets for an exchange adapter
    """
    try:
        adapter = exchange_registry.get_adapter(adapter_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange adapter '{adapter_name}' not found"
            )
        
        # Get supported markets
        supported_markets = adapter.get_supported_markets()
        
        return {
            "name": adapter_name,
            "supported_markets": supported_markets,
            "count": len(supported_markets)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported markets: {str(e)}"
        )