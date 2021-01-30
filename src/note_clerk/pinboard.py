"""Command-line interface."""
import datetime as dt
from inspect import cleandoc as trim
from pathlib import Path

import click
from dateutil.tz import tzlocal
import pinboard


@click.command()
@click.option("--api-token", required=True, envvar="PINBOARD_TOKEN")
@click.option("--note-dir", default=".", type=click.Path())
@click.option("--write-notes/--dry-run", default=False)
def download(api_token: str, note_dir: Path, write_notes: bool) -> None:
    pb = pinboard.Pinboard(api_token)
    if isinstance(note_dir, str):
        note_dir = Path(note_dir)

    pins = pb.posts.all(results=10)
    now = dt.datetime.now(tzlocal())
    for pin in pins:
        note = note_dir / f"{pin.time:%Y%m%d%H%M%S}.md"
        movement = dt.timedelta()
        while note.exists():
            movement += dt.timedelta(seconds=1)
            note = note_dir / f"{pin.time + movement:%Y%m%d%H%M%S}.md"

        if movement > dt.timedelta():
            print(
                f"Prevented collision: '{pin.time:%Y%m%d%H%M%S}.md'"
                f" -> '{pin.time + movement:%Y%m%d%H%M%S}.md'"
            )

        tags = [t for t in pin.tags if t.strip() != ""]
        if pin.toread:
            tags.append("todo-read")
        if pin.shared is False:
            tags.append(".private")

        fmtd_tags = [f'"#{t.replace(" ", "-")}"' for t in tags]
        note_content = (
            trim(
                f"""
            ---
            created: {now:%Y-%m-%dT%H:%M:%S%z}
            type: resource/link
            tags: [{', '.join(fmtd_tags)}]
            pinboard:
              time: {pin.time:%Y-%m-%dT%H:%M:%S%z}
              shared: {str(pin.shared).lower()}
              hash: {pin.hash}
              change_id: {pin.meta}
            ---
            # {pin.description}
            **URL:** {pin.url}
            """
            )
            + "\n\n"
        )

        note_content += pin.extended
        note_content = note_content.replace("tags: []\n", "").strip() + "\n"

        if write_notes:
            with note.open("w") as f:
                f.write(note_content)
