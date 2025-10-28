import xml.etree.ElementTree as ET
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
            url = "/ocs/v1.php/cloud/users"
            params = {}

            if search:
                params["search"] = search
            if limit:
                params["limit"] = limit
            if offset:
                params["offset"] = offset

            # Send GET request with OCS-APIRequest header
            response = self._request(
                "GET", url, headers={"OCS-APIRequest": "true"}, params=params
            )

            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)

                # Check status
                statuscode = root.find(".//statuscode")
                if statuscode is not None and statuscode.text == "100":
                    # Extract list of users
                    users = []
                    for user_elem in root.findall(".//users/element"):
                        if user_elem.text:
                            users.append(user_elem.text)

                    return users
                else:
                    # Get error message
                    message = root.find(".//message")
                    if message is not None:
                        raise ValueError(f"OCS error: {message.text}")
                    raise ValueError("Failed to retrieve users list")
            else:
                raise HTTPError(
                    f"HTTP error: {response.status_code} - {response.text}",
                    response=response,
                )

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}") from e
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
            url = f"/ocs/v1.php/cloud/users/{userid}"

            # Send GET request with OCS-APIRequest header
            response = self._request("GET", url, headers={"OCS-APIRequest": "true"})

            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)

                # Check status
                statuscode = root.find(".//statuscode")
                if statuscode is not None and statuscode.text == "100":
                    # Extract all user data
                    user_data = {}
                    data_elem = root.find(".//data")

                    if data_elem is not None:
                        # Get all user fields
                        for child in data_elem:
                            tag_name = child.tag

                            # Process groups separately
                            if tag_name == "groups":
                                groups = []
                                for group_elem in child.findall(".//element"):
                                    if group_elem.text:
                                        groups.append(group_elem.text)
                                user_data["groups"] = groups
                            else:
                                user_data[tag_name] = child.text if child.text else ""

                    return user_data
                else:
                    # Get error message
                    message = root.find(".//message")
                    if message is not None:
                        raise ValueError(f"OCS error: {message.text}")
                    raise ValueError("Failed to retrieve user data")
            elif response.status_code == 404:
                raise HTTPError(f"User not found: {userid}", response=response)
            else:
                raise HTTPError(
                    f"HTTP error: {response.status_code} - {response.text}",
                    response=response,
                )

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to retrieve user data: {e}") from e
