import { message } from 'antd';
import { Report } from '../types/report';

// 导出报表为CSV格式
export const exportReportToCSV = (report: Report, filename: string = 'report.csv') => {
  try {
    // 创建CSV内容
    let csvContent = '';
    
    // 添加表头
    if (report.trades && report.trades.length > 0) {
      const headers = Object.keys(report.trades[0]);
      csvContent += headers.join(',') + '\n';
      
      // 添加数据行
      report.trades.forEach(trade => {
        const values = headers.map(header => {
          let value = trade[header as keyof typeof trade];
          if (typeof value === 'string') {
            // 转义包含逗号或引号的字符串
            if (value.includes(',') || value.includes('"')) {
              value = `"${value.replace(/"/g, '""')}"`;
            }
          }
          return value;
        });
        csvContent += values.join(',') + '\n';
      });
    }
    
    // 创建并下载文件
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    message.success('报表导出成功');
  } catch (error) {
    console.error('Export error:', error);
    message.error('报表导出失败');
  }
};

// 导出报表为Excel格式
export const exportReportToExcel = (report: Report, filename: string = 'report.xlsx') => {
  message.warning('Excel导出功能待实现');
  // 在实际实现中，我们会使用像xlsx这样的库来生成Excel文件
};

// 导出报表为PDF格式
export const exportReportToPDF = (report: Report, filename: string = 'report.pdf') => {
  message.warning('PDF导出功能待实现');
  // 在实际实现中，我们会使用像jspdf这样的库来生成PDF文件
};

// 通用导出函数
export const exportReport = (report: Report, format: 'csv' | 'excel' | 'pdf', filename?: string) => {
  switch (format) {
    case 'csv':
      return exportReportToCSV(report, filename || `${report.name}.csv`);
    case 'excel':
      return exportReportToExcel(report, filename || `${report.name}.xlsx`);
    case 'pdf':
      return exportReportToPDF(report, filename || `${report.name}.pdf`);
    default:
      message.error('不支持的导出格式');
  }
};