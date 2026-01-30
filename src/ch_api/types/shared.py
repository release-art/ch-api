"""Shared data types and utilities for Companies House API responses.

This module contains Pydantic models and utilities used across multiple
API response types, providing common patterns and reusable components.

Shared Components
-----
- :class:`LinksSection` - Links to related API resources in responses

These types are used by multiple API response models to represent common
elements like resource links.

Example
-------
Access links from an API response::

    company = await client.get_company_profile("09370755")
    if company.links and company.links.self:
        print(f"Company profile: {company.links.self}")

See Also
--------
ch_api.types.base : Base model configuration
ch_api.types.public_data : Models using these shared types
"""

import pydantic

from . import base


class LinksSection(base.BaseModel):
    """Links to related API resources in response objects.

    This model represents the ``_links`` section commonly found in Companies House
    API responses. It provides convenient access to related resource endpoints
    via the ``self`` link and other related links.

    The model allows arbitrary link properties to be added, accommodating various
    API response structures that include different sets of links.

    Attributes
    ----------
    Any string properties starting with ``/`` or containing URLs represent links
    to related resources. Examples include:

    - ``self`` - Link to the current resource
    - ``company`` - Link to the company resource
    - ``officer`` - Link to officer resource
    - And other resource-specific links

    Configuration
    -----
    - **Extra fields allowed**: Can contain any additional link fields from API responses
    - **Field mapping**: Uses Pydantic's extra field handling for dynamic links

    Example
    -------
    Access links from an API response::

        company = await client.get_company_profile("09370755")

        # Get the self link
        if company.links:
            self_url = company.links.self
            print(f"Self: {self_url}")

            # Get custom link by name
            custom_link = company.links.get_link("company")
            if custom_link:
                print(f"Company: {custom_link}")

    Properties
    ----------
    self : str | None
        The URL of the current resource. Read-only property that retrieves
        the 'self' link from the links section.

    Methods
    -------
    get_link(name: str) -> str | None
        Retrieve a link by name from the links section. Returns None if
        the link doesn't exist.

    Note
    ----
    The ``_links`` section in API responses is included as ``links`` in the
    Python models for consistency with Python naming conventions (avoiding
    leading underscores for public attributes).

    See Also
    --------
    pydantic.BaseModel : Parent Pydantic model
    """

    model_config = pydantic.ConfigDict(
        extra="allow",
    )

    @property
    def self(self) -> str | None:
        """Get the 'self' link from the links section.

        This property provides convenient access to the self link, which
        points to the current resource in the API.

        Returns
        -------
        str | None
            The URL of the 'self' link if it exists, otherwise None.
            The URL typically starts with ``https://api.company-information.service.gov.uk/``

        Example
        -------
        Get the self link::

            >>> from ch_api.types.shared import LinksSection
            >>> links = LinksSection(self="https://api.company-information.service.gov.uk/company/09370755")
            >>> if links and links.self:
            ...     url = links.self
            ...     print(f"Resource: {url}")
            Resource: https://api.company-information.service.gov.uk/company/09370755
        """
        return self.get_link("self")

    def get_link(self, name: str) -> str | None:
        """Get a link by name from the links section.

        Retrieves a specific link from the response's ``_links`` section by name.
        This allows accessing both standard links (like 'self') and API-specific
        links defined in the response.

        Parameters
        ----------
        name : str
            The name of the link to retrieve. Standard link names include:

            - ``self`` - The current resource
            - ``company`` - The company resource
            - ``officer`` - The officer resource
            - And other resource-specific links

        Returns
        -------
        str | None
            The URL of the requested link if it exists in the response,
            otherwise None. URLs are typically full HTTPS paths to API endpoints.

        Example
        -------
        Get various links::

            links = response.links
            self_url = links.get_link("self")
            company_url = links.get_link("company")

        Note
        ----
        This method uses Pydantic's ``__pydantic_extra__`` to access dynamically
        defined link fields that aren't explicitly declared in the model.

        See Also
        --------
        self : Property for getting the 'self' link
        """
        if self.__pydantic_extra__ is None:
            return None
        return self.__pydantic_extra__.get(name, None)
