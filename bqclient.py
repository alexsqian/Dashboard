from googleapiclient.discovery import build

class BigQueryClient(object):
    def __init__(self, http):
        """Creates the BigQuery client connection"""
        self.http = http
        self.service = build('bigquery', 'v2', http=http)
        # self.decorator = decorator

    def Query(self, query, project, timeout_ms=10000):
        query_config = {
            'query': query,
            'timeoutMs': timeout_ms
        }
        query_http = self.http
        result_json = (self.service.jobs().query(projectId=project, body=query_config).execute(query_http))
        return result_json
