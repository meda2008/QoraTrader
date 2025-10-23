// frontend/src/services/riskRuleService.ts

import { RiskParams } from '../types/risk';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

class RiskRuleService {
  static async getRiskRules(): Promise<RiskParams[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/risk-rules`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add auth token if needed
          // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching risk rules:', error);
      throw error;
    }
  }

  static async createRiskRule(riskRule: Omit<RiskParams, 'id' | 'created_at' | 'updated_at'>): Promise<RiskParams> {
    try {
      const response = await fetch(`${API_BASE_URL}/risk-rules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add auth token if needed
          // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(riskRule),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating risk rule:', error);
      throw error;
    }
  }

  static async updateRiskRule(id: string, riskRule: Partial<RiskParams>): Promise<RiskParams> {
    try {
      const response = await fetch(`${API_BASE_URL}/risk-rules/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          // Add auth token if needed
          // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(riskRule),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating risk rule:', error);
      throw error;
    }
  }

  static async deleteRiskRule(id: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/risk-rules/${id}`, {
        method: 'DELETE',
        headers: {
          // Add auth token if needed
          // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error deleting risk rule:', error);
      throw error;
    }
  }
}

export { RiskRuleService };