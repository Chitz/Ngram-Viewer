from .base import BaseChart


class BaseGChart(BaseChart):
    def get_html_template(self):
        return "chart/html.html"


class LineChart(BaseGChart):
    def get_js_template(self):
        return "chart/line_chart.html"