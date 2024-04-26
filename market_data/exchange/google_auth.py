import warnings
warnings.filterwarnings('ignore')
import gspread
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')

from google.cloud import cloudquotas_v1


def sample_get_quota_info():
    # Create a client
    client = cloudquotas_v1.CloudQuotasClient()

    # Initialize request argument(s)
    request = cloudquotas_v1.GetQuotaInfoRequest(
        name="name_value",
    )

    # Make the request
    response = client.get_quota_info(request=request)

    # Handle the response
    print(response)
sample_get_quota_info()