PROJECT=$(shell gcloud config get-value project)
FUNCIONS_REGION=$(shell gcloud config get-value functions/region)
SCHEDULER_TIME_ZONE=Etc/UTC

test:
	python -m pytest

deploy:
	gcloud --project ${PROJECT} functions deploy load_gcs_to_bigquery \
		--region ${FUNCIONS_REGION} \
		--trigger-topic load_gcs_to_bigquery \
		--timeout 540 \
		--memory 4096 \
		--runtime python37
	
	gcloud --project ${PROJECT} functions deploy tidyup_bigquery \
		--region ${FUNCIONS_REGION} \
		--trigger-topic tidyup_bigquery \
		--runtime python37

install-scheduler: install-scheduler-check-env
	gcloud --project ${PROJECT} pubsub topics create load_gcs_to_bigquery
	gcloud --project ${PROJECT} scheduler jobs create pubsub load_gcs_to_bigquery \
		--description 'Load profiling data to BigQuery' \
		--schedule "0 * * * *" \
		--topic load_gcs_to_bigquery \
		--time-zone ${SCHEDULER_TIME_ZONE} \
		--message-body '' \
		--attributes 'bucket=${SRC_BUCKET},name=performance_profile/'
	
	gcloud --project ${PROJECT} pubsub topics create tidyup_bigquery
	gcloud --project ${PROJECT} scheduler jobs create pubsub tidyup_bigquery \
		--description 'Tidyup BigQuery' \
		--schedule "0 0 * * *" \
		--topic tidyup_bigquery \
		--time-zone ${SCHEDULER_TIME_ZONE} \
		--message-body 'dummy'

install-scheduler-check-env:
ifndef SRC_BUCKET
	$(error SRC_BUCKET is undefined)
endif
