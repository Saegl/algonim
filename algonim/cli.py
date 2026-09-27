import sys
from argparse import ArgumentParser
from pathlib import Path

import pyglet

from algonim.resolution import RESOLUTIONS, Resolution

OUTPUT_DIR = Path("output")


def main():
    parser = ArgumentParser(
        "algonim",
        description="Script-first animation engine",
        epilog="Mode defaults to preview: algonim <script> is algonim preview <script>",
    )
    modes = parser.add_subparsers(dest="mode", required=True)

    preview = modes.add_parser(
        "preview", help="Play in a window: Space pauses, F3 dev mode, Q quits"
    )
    video = modes.add_parser("video", help="Render headless to a video file")
    for mode, default_resolution in ((preview, "900p"), (video, "1080p")):
        mode.add_argument("script", type=Path, help="Path to video script")
        mode.add_argument(
            "-r",
            "--resolution",
            choices=RESOLUTIONS,
            default=default_resolution,
            help="16:9 preset, scripts use 1600x900 coordinates at any of them "
            f"(default {default_resolution})",
        )
    video.add_argument(
        "-o",
        "--output",
        type=Path,
        help=f"Video path (default {OUTPUT_DIR}/<script>-<resolution>.mp4)",
    )

    argv = sys.argv[1:]
    if argv and argv[0] not in (*modes.choices, "-h", "--help"):
        argv.insert(0, "preview")
    args = parser.parse_args(argv)
    resolution = Resolution.preset(args.resolution)

    if args.mode == "preview":
        from algonim.render import preview

        preview(args.script, resolution)
    else:
        output = args.output or OUTPUT_DIR / f"{args.script.stem}-{args.resolution}.mp4"
        output.parent.mkdir(parents=True, exist_ok=True)
        # Must be set before pyglet creates its window module
        pyglet.options["headless"] = True
        from algonim.render import render_video

        render_video(args.script, resolution, output)
        print(f"Saved {output}")
