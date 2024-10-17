"""
This module contains stubs for the audio processing functions.
"""

from typing import BinaryIO, Union


def decode_audio(
    input_file: Union[str, BinaryIO],
    sampling_rate: int = 16000,
    split_stereo: bool = False,
):
    return []


def pad_or_trim(array, length: int, *, axis: int = -1):
    return []
