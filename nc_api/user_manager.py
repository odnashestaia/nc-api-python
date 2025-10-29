import json
from typing import Dict, List, Optional, Union

from requests import HTTPError

from nc_api.base_manager import BaseManager


class UserManager(BaseManager):
    def __init__(self, NEXTCLOUD_URL: str, USERNAME: str, PASSWORD: str) -> None:
        super().__init__(NEXTCLOUD_URL, USERNAME, PASSWORD)

    def get_users(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Union[List[str], str]:
        """
        Retrieves list of users from Nextcloud via OCS API.

        :param search: Optional search filter
        :param limit: Optional limit
        :param offset: Optional offset
        :return: List of usernames or error string
        """
        try:
            # Build URL with parameters
            url = "ocs/v1.php/cloud/users?format=json"
            params = {}

            if search:
                params["search"] = search
            if limit:
                params["limit"] = limit
            if offset:
                params["offset"] = offset

            # Send GET request with OCS-APIRequest header
            response = self._request_webdav(
                "GET",
                url,
                headers={"OCS-APIRequest": "true"},
                params=params,
                is_rest=True,
            )

            if response.status_code in [200, 201, 207, 206]:
                # Parse JSON response
                return json.loads(response.text)
            else:
                raise HTTPError(
                    f"HTTP error: {response.status_code} - {response.text}",
                    response=response,
                )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to retrieve users list: {e}") from e

    def get_user(
        self,
        username: Optional[str] = None,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Union[Dict[str, str], str]:
        """
        Retrieves full user data via OCS API for a specific user.

        :param username: Optional username (login)
        :param user_id: Optional user ID
        :param name: Optional display name
        :return: Dict with user data or error string
        """
        try:
            # Resolve userid from given parameters
            userid = None
            if username:
                userid = username
            elif user_id:
                userid = user_id
            elif name:
                userid = name
            else:
                raise ValueError("One of username, user_id or name must be provided")

            # Build URL for specific user
            url = f"/ocs/v1.php/cloud/users/{userid}?format=json"

            # Send GET request with OCS-APIRequest header
            response = self._request_webdav(
                "GET",
                url,
                headers={"OCS-APIRequest": "true"},
                is_rest=True,
            )

            if response.status_code in [200, 201, 207, 206]:
                # Parse JSON response
                return json.loads(response.text)
            elif response.status_code == 404:
                raise HTTPError(f"User not found: {userid}", response=response)
            else:
                raise HTTPError(
                    f"HTTP error: {response.status_code} - {response.text}",
                    response=response,
                )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to retrieve user data: {e}") from e
