"""
Testes para o serviço de análise de energia
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.services.energy_service import EnergyAnalysisService
from src.models.database import Device, EnergyReading, DailyReport


@pytest.fixture
def energy_service():
    """Fixture para o serviço de energia"""
    return EnergyAnalysisService()


@pytest.fixture
def mock_device():
    """Fixture para dispositivo mock"""
    device = Mock(spec=Device)
    device.id = 1
    device.name = "Geladeira"
    device.type = "TAPO"
    device.location = "Cozinha"
    device.equipment_connected = "Geladeira Consul"
    return device


@pytest.fixture
def mock_energy_readings():
    """Fixture para leituras de energia mock"""
    readings = []
    base_time = datetime.utcnow()
    
    for i in range(24):  # 24 horas de dados
        for j in range(4):  # 4 leituras por hora
            reading = Mock(spec=EnergyReading)
            reading.timestamp = base_time + timedelta(hours=i, minutes=j*15)
            reading.power_watts = 50 + (i * 2) + (j * 0.5)  # Consumo variando
            reading.voltage = 220
            reading.current = reading.power_watts / 220
            readings.append(reading)
    
    return readings


class TestEnergyAnalysisService:
    """Classe de testes para EnergyAnalysisService"""
    
    def test_init(self, energy_service):
        """Testar inicialização do serviço"""
        assert energy_service.cost_per_kwh == 0.85
        assert hasattr(energy_service, 'cost_per_kwh')
    
    @patch('src.services.energy_service.get_db')
    def test_calculate_daily_consumption_success(self, mock_get_db, energy_service, mock_device, mock_energy_readings):
        """Testar cálculo de consumo diário com sucesso"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock query readings
        mock_db.query.return_value.filter.return_value.all.return_value = mock_energy_readings
        
        # Executar teste
        result = energy_service.calculate_daily_consumption(mock_device.id, datetime.utcnow())
        
        # Verificações
        assert result is not None
        assert result['device_id'] == mock_device.id
        assert result['total_energy_kwh'] > 0
        assert result['total_cost'] > 0
        assert result['readings_count'] == len(mock_energy_readings)
        assert result['peak_power_watts'] >= result['average_power_watts']
        assert result['peak_power_watts'] >= result['min_power_watts']
    
    @patch('src.services.energy_service.get_db')
    def test_calculate_daily_consumption_no_readings(self, mock_get_db, energy_service, mock_device):
        """Testar cálculo quando não há leituras"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock query sem leituras
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Executar teste
        result = energy_service.calculate_daily_consumption(mock_device.id, datetime.utcnow())
        
        # Verificações
        assert result is None
    
    @patch('src.services.energy_service.get_db')
    def test_detect_anomalies_above_threshold(self, mock_get_db, energy_service, mock_device):
        """Testar detecção de anomalias acima do threshold"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock média histórica baixa
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50.0
        
        # Consumo atual muito alto
        current_consumption = 200.0
        
        # Executar teste
        result = energy_service.detect_anomalies(mock_device.id, current_consumption)
        
        # Verificações
        assert result is not None
        assert result['current_consumption'] == current_consumption
        assert result['average_consumption'] == 50.0
        assert result['anomaly_factor'] == 4.0  # 200/50
        assert 'anomaly' in result['description'].lower()
    
    @patch('src.services.energy_service.get_db')
    def test_detect_anomalies_normal_consumption(self, mock_get_db, energy_service, mock_device):
        """Testar detecção quando consumo é normal"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock média histórica
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50.0
        
        # Consumo atual normal
        current_consumption = 60.0
        
        # Executar teste
        result = energy_service.detect_anomalies(mock_device.id, current_consumption)
        
        # Verificações
        assert result is None
    
    @patch('src.services.energy_service.get_db')
    def test_generate_daily_report(self, mock_get_db, energy_service, mock_device, mock_energy_readings):
        """Testar geração de relatório diário"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock dispositivos
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_device]
        
        # Mock leituras e cálculos
        with patch.object(energy_service, 'calculate_daily_consumption') as mock_calc, \
             patch.object(energy_service, 'detect_anomalies') as mock_anomaly:
            
            mock_calc.return_value = {
                'device_id': mock_device.id,
                'total_energy_kwh': 2.5,
                'total_cost': 2.12,
                'peak_power_watts': 150.0,
                'average_power_watts': 60.0,
                'min_power_watts': 30.0,
                'runtime_hours': 12.0
            }
            
            mock_anomaly.return_value = None
            
            # Executar teste
            result = energy_service.generate_daily_report()
            
            # Verificações
            assert result is not None
            assert 'date' in result
            assert 'devices' in result
            assert 'total_energy_kwh' in result
            assert 'total_cost' in result
            assert len(result['devices']) == 1
            assert result['total_energy_kwh'] == 2.5
            assert result['total_cost'] == 2.12
    
    @patch('src.services.energy_service.get_db')
    def test_get_realtime_status(self, mock_get_db, energy_service, mock_device):
        """Testar obtenção de status em tempo real"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        # Mock dispositivos
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_device]
        
        # Mock última leitura
        mock_reading = Mock(spec=EnergyReading)
        mock_reading.power_watts = 75.5
        mock_reading.timestamp = datetime.utcnow()
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_reading
        
        # Executar teste
        result = energy_service.get_realtime_status()
        
        # Verificações
        assert result is not None
        assert 'timestamp' in result
        assert 'devices' in result
        assert 'total_current_power_watts' in result
        assert 'active_devices' in result
        assert len(result['devices']) == 1
        assert result['total_current_power_watts'] == 75.5
        assert result['active_devices'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
