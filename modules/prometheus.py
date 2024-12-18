from prometheus_client import start_http_server, Summary, Gauge

class MetricsGenerator():
    def __init__(self) -> None:
        self.gauges = {}

    def create_gauge(self, name, desc):
        """Gaugeの新規登録用"""
        if name in self.gauges:
            raise ValueError(f"Gauge '{name}' は既に登録されています。")
        self.gauges[name] = Gauge(name, desc)
        return self.gauges[name]
    
    def increment(self, name, value=1):
        """指定したGaugeに加算"""
        if name not in self.gauges:
            raise KeyError(f"Gauge '{name}' は存在しません")
        self.gauges[name].inc(value)

    def set(self, name, value):
        """指定したGaugeに設定"""
        if name not in self.gauges:
            raise KeyError(f"Gauge '{name}' は存在しません")
        self.gauges[name].set(value)

    def get(self, name):
        """指定したGaugeを取得"""
        if name not in self.gauges:
            raise KeyError(f"Gauge '{name}' は存在しません")
        self.gauges[name]

def start(port: int = 5001, ip: str = "0.0.0.0"):
    start_http_server(port, ip)