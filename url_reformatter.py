import numpy as np, requests
from typing import Iterable

def reformat_with_timestamps(url: str, timestamps: Iterable[float]):
    """
    Create separate URL for different timestamps from the same video url.
    """
    response = requests.get(url=url)
    assert response.status_code == 200
    print(response.status_code)
    return np.asarray(a=list([url + f'&t={ts}s' for ts in timestamps]))

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=werwaerfsadf'
    ts_urls = reformat_with_timestamps(url=url, timestamps=[10, 20, 30, 60])
    print(ts_urls)