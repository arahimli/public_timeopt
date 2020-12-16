from google.cloud import bigquery

def run_quickstart():
    # [START bigquery_quickstart]
    # Imports the Google Cloud client library
    from google.cloud import bigquery

    # Instantiates a client
    bigquery_client = bigquery.Client()

    # The name for the new dataset
    dataset_id = 'my_new_dataset'

    # Prepares a reference to the new dataset
    dataset_ref = bigquery_client.dataset(dataset_id)
    dataset = bigquery.Dataset(dataset_ref)

    # Creates the new dataset
    dataset = bigquery_client.create_dataset(dataset)

    print('Dataset {} created.'.format(dataset.dataset_id))
    # [END bigquery_quickstart]


if __name__ == '__main__':
    run_quickstart()



