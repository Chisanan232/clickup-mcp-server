"""
Time Report DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Time Report resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic TimeReport domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto)
4. Domain Entity → MCP Output (to_time_report_result_output, to_time_report_list_item_output)

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

    report_domain = ReportingMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    report_domain = ReportingMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = ReportingMapper.to_create_dto(report_domain)

    # Python - Map domain to MCP output
    mcp_output = ReportingMapper.to_time_report_result_output(report_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.reporting import TimeReport
from clickup_mcp.models.dto.reporting import TimeReportCreate, TimeReportResponse

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.reporting import (
        TimeReportCreateInput,
    )


class ReportingMapper:
    """
    Static mapper for converting between Time Report DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Time Report data:

    1. **MCP Input → Domain**: Converts user-facing MCP input models to domain entities
    2. **API Response → Domain**: Converts ClickUp API responses to domain entities
    3. **Domain → API Request**: Converts domain entities to ClickUp API request DTOs
    4. **Domain → MCP Output**: Converts domain entities to user-facing MCP output models

    Key Design Principles:
    - **Separation of Concerns**: Domain logic is isolated from transport details
    - **Unidirectional Flow**: Data flows in one direction through the mapper
    - **Testability**: Each mapping can be tested independently
    - **Maintainability**: Changes to DTOs don't affect domain logic

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Create a time report from MCP input
        from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

        mcp_input = TimeReportCreateInput(
            team_id="team_1",
            start_date=1702080000000,
            end_date=1702166400000
        )
        report_domain = ReportingMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        report_domain = ReportingMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = ReportingMapper.to_create_dto(report_domain)

        # Python - Return to MCP client
        mcp_output = ReportingMapper.to_time_report_result_output(report_domain)
    """

    @staticmethod
    def from_create_input(input: "TimeReportCreateInput") -> TimeReport:
        """
        Map MCP TimeReportCreateInput to TimeReport domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the time report in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual report is created via API.

        Args:
            input: TimeReportCreateInput from MCP tool call containing:
                - team_id: Team/workspace ID (required)
                - start_date: Start date in epoch ms (required)
                - end_date: End date in epoch ms (required)
                - assignee: Filter by user ID (optional)
                - task_id: Filter by task ID (optional)

        Returns:
            TimeReport domain entity with:
                - report_id: Temporary placeholder "temp" (will be replaced after API creation)
                - team_id: From input.team_id
                - start_date: From input.start_date
                - end_date: From input.end_date
                - total_duration: None (calculated by API)
                - user_id: From input.assignee
                - task_id: From input.task_id

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

            mcp_input = TimeReportCreateInput(
                team_id="team_1",
                start_date=1702080000000,
                end_date=1702166400000
            )
            report = ReportingMapper.from_create_input(mcp_input)
            # report.report_id == "temp"
            # report.team_id == "team_1"
            # report.start_date == 1702080000000
        """
        return TimeReport(
            id="temp",
            team_id=input.team_id,
            start_date=input.start_date,
            end_date=input.end_date,
            total_duration=None,
            user_id=input.assignee,
            task_id=input.task_id,
        )

    @staticmethod
    def to_domain(resp: TimeReportResponse) -> TimeReport:
        """
        Map ClickUp API response DTO to TimeReport domain entity.

        Converts the ClickUp API response (TimeReportResponse DTO) to a domain entity,
        extracting relevant fields. This is the primary entry point for API responses.

        Args:
            resp: TimeReportResponse DTO from ClickUp API containing:
                - id: Time report ID
                - team_id: Team/workspace ID
                - start_date: Start date in epoch milliseconds
                - end_date: End date in epoch milliseconds
                - total_duration: Total duration in milliseconds
                - user_id: Filter by user ID
                - task_id: Filter by task ID

        Returns:
            TimeReport domain entity with:
                - report_id: From resp.id
                - team_id: From resp.team_id
                - start_date: From resp.start_date
                - end_date: From resp.end_date
                - total_duration: From resp.total_duration
                - user_id: From resp.user_id
                - task_id: From resp.task_id

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper
            from clickup_mcp.models.dto.reporting import TimeReportResponse

            api_response = TimeReportResponse(
                id="report_123",
                team_id="team_001",
                start_date=1702080000000,
                end_date=1702166400000,
                total_duration=3600000
            )
            report = ReportingMapper.to_domain(api_response)
            # report.report_id == "report_123"
            # report.team_id == "team_001"
            # report.total_duration == 3600000
        """
        return TimeReport(
            id=resp.id,
            team_id=resp.team_id,
            start_date=resp.start_date,
            end_date=resp.end_date,
            total_duration=resp.total_duration,
            user_id=resp.user_id,
            task_id=resp.task_id,
        )

    @staticmethod
    def to_create_dto(report: TimeReport) -> TimeReportCreate:
        """
        Map TimeReport domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a time report.

        Args:
            report: TimeReport domain entity containing report data

        Returns:
            TimeReportCreate DTO with:
                - start_date: From report.start_date
                - end_date: From report.end_date
                - assignee: From report.user_id
                - task_id: From report.task_id

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

            report = TimeReport(
                id="temp",
                team_id="team_001",
                start_date=1702080000000,
                end_date=1702166400000
            )
            create_dto = ReportingMapper.to_create_dto(report)
            # create_dto.start_date == 1702080000000
            # create_dto.end_date == 1702166400000

            # Python - Use with API client
            response = await client.time.create_report(
                team_id="team_001",
                report_create=create_dto
            )
        """
        return TimeReportCreate(
            start_date=report.start_date,
            end_date=report.end_date,
            assignee=report.user_id,
            task_id=report.task_id,
        )

    @staticmethod
    def to_time_report_result_output(report: TimeReport) -> dict:
        """
        Map TimeReport domain entity to MCP time report result output.

        Converts a domain entity to the MCP output format for returning
        time report details to the MCP client. This is used for single report
        responses (get, create operations).

        Args:
            report: TimeReport domain entity to convert

        Returns:
            Dictionary with time report data:
                - id: From report.report_id
                - team_id: From report.team_id
                - start_date: From report.start_date
                - end_date: From report.end_date
                - total_duration: From report.total_duration
                - user_id: From report.user_id
                - task_id: From report.task_id

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

            report = TimeReport(
                id="report_123",
                team_id="team_001",
                start_date=1702080000000,
                end_date=1702166400000,
                total_duration=3600000
            )
            mcp_output = ReportingMapper.to_time_report_result_output(report)
            # mcp_output["id"] == "report_123"
            # mcp_output["team_id"] == "team_001"

            # Python - Return from MCP tool
            return mcp_output
        """
        return {
            "id": report.report_id,
            "team_id": report.team_id,
            "start_date": report.start_date,
            "end_date": report.end_date,
            "total_duration": report.total_duration,
            "user_id": report.user_id,
            "task_id": report.task_id,
        }

    @staticmethod
    def to_time_report_list_item_output(report: TimeReport) -> dict:
        """
        Map TimeReport domain entity to MCP time report list item output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple reports
        in a list.

        Args:
            report: TimeReport domain entity to convert

        Returns:
            Dictionary with time report list item data:
                - id: From report.report_id
                - team_id: From report.team_id
                - start_date: From report.start_date
                - end_date: From report.end_date
                - total_duration: From report.total_duration

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

            report = TimeReport(
                id="report_123",
                team_id="team_001",
                start_date=1702080000000,
                end_date=1702166400000,
                total_duration=3600000
            )
            list_item = ReportingMapper.to_time_report_list_item_output(report)
            # list_item["id"] == "report_123"
            # list_item["team_id"] == "team_001"

            # Python - Return from MCP tool (in a list)
            reports = [ReportingMapper.to_time_report_list_item_output(r) for r in domain_reports]
            return reports
        """
        return {
            "id": report.report_id,
            "team_id": report.team_id,
            "start_date": report.start_date,
            "end_date": report.end_date,
            "total_duration": report.total_duration,
        }
