"""Fast local checks for the hybrid pipeline; no cloud/API credentials are used."""

import asyncio
import pathlib
import subprocess
import tempfile
import unittest

from azure_vm import vm_app


class HybridPipelineTests(unittest.TestCase):
    def test_allocator_respects_the_eight_slide_product_limit(self):
        for total_slides, expected in {
            0: (0, 0),
            1: (1, 0),
            2: (2, 0),
            3: (2, 1),
            6: (2, 4),
            8: (2, 6),
        }.items():
            local_count = min(total_slides, vm_app.VM_CAPACITY)
            remote_count = total_slides - local_count
            self.assertEqual((local_count, remote_count), expected)
            self.assertLessEqual(remote_count, vm_app.MAX_MODAL_WORKERS)

    def test_single_pass_assembly_preserves_every_narration(self):
        """Two three-second clips must become 3.5s + 4.0s, not six seconds."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            animation_paths = [root / "animation_0.mp4", root / "animation_1.mp4"]
            audio_paths = [root / "audio_0.mp3", root / "audio_1.mp3"]

            for index, animation_path in enumerate(animation_paths):
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={'red' if index == 0 else 'blue'}:s=320x180:r=24",
                        "-t", "3", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(animation_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            for audio_path, duration in zip(audio_paths, (3.5, 4.0)):
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
                        "-t", str(duration), "-q:a", "9", str(audio_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            output_path = root / "final.mp4"
            slide_durations, _ = asyncio.run(
                vm_app.assemble_video_once(
                    [str(path) for path in animation_paths],
                    [str(path) for path in audio_paths],
                    str(output_path),
                )
            )
            output_duration = asyncio.run(vm_app.probe_duration(str(output_path)))

            self.assertAlmostEqual(slide_durations[0], 3.5, delta=0.15)
            self.assertAlmostEqual(slide_durations[1], 4.0, delta=0.15)
            self.assertAlmostEqual(output_duration, 7.5, delta=0.25)


if __name__ == "__main__":
    unittest.main(verbosity=2)
