from typing import List, Optional, Type

from common import directories
from common.colorize_tex import ColorizeOptions
from common.commands.base import Command, CommandList
from common.commands.detect_entities import make_detect_entities_command
from common.commands.locate_entities import make_locate_entities_command, ColorizeFunc
from common.commands.upload_entities import make_upload_entities_command
from common.parse_tex import EntityExtractor
from common.types import EntityUploadCallable, SerializableEntity


def create_entity_localization_command_sequence(
    entity_name: str,
    EntityExtractorType: Type[EntityExtractor],
    DetectedEntityType: Optional[Type[SerializableEntity]] = None,
    upload_func: Optional[EntityUploadCallable] = None,
    colorize_options: ColorizeOptions = ColorizeOptions(),
    colorize_func: Optional[ColorizeFunc] = None,
) -> List[Type[Command]]:  # type: ignore
    """
    Create a set of commands that can be used to locate a new type of entity. In the simplest case,
    all you have to provide is and 'entity_name' to be used for naming output files, and
    'entity_type' that can be used to filter which commands are being run when you the full
    pipeline is run, and an 'EntityExtractorType' that locates all instances of that entity in the
    TeX. This function creates the commands necessary to colorize the entities, compile the
    LaTeX, raster the pages, and locate the colors in the pages. You may define additional
    paramters (e.g., 'colorize_options') to fine-tune the commands.

    If you are trying to find the locations of a new type of entity, it is highly recommended that
    you use this convenience methods instead of creating new commands yourself.
    """

    # Register directories for output from intermediate pipeline stages.
    directories.register(f"detected-{entity_name}")
    directories.register(f"sources-with-colorized-{entity_name}")
    directories.register(f"compiled-sources-with-colorized-{entity_name}")
    directories.register(f"paper-images-with-colorized-{entity_name}")
    directories.register(f"diffed-images-with-colorized-{entity_name}")
    directories.register(f"{entity_name}-locations")

    commands: CommandList = [
        make_detect_entities_command(entity_name, EntityExtractorType),
        make_locate_entities_command(
            entity_name, DetectedEntityType, colorize_options, colorize_func
        ),
    ]

    if upload_func is not None:
        upload_command = make_upload_entities_command(
            entity_name, upload_func, DetectedEntityType=DetectedEntityType
        )
        commands.append(upload_command)

    return commands
