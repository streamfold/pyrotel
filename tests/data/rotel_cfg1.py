from rotel import Rotel, OTLPExporter

rotel = Rotel(
    otlp_grpc_port = 5317,
    exporter = OTLPExporter(
        endpoint = "http://{OTLP_API}:4317",
        compression = "gzip",
        custom_headers = ["api-key={API_KEY}", "team={TEAM_NAME}"]
    )
)
