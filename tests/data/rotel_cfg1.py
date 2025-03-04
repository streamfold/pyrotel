from rotel import OTLPExporter, Rotel


rotel = Rotel(
    enabled = True,
    otlp_grpc_endpoint = "localhost:5317",
    exporter = OTLPExporter(
        endpoint = "http://{OTLP_API}:4317",
        compression = "gzip",
        custom_headers = ["api-key={API_KEY}", "team={TEAM_NAME}"]
    )
)
