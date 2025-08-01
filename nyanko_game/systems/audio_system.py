# -*- coding: utf-8 -*-
"""
音效系統
負責遊戲中所有音效和背景音樂的播放管理
"""

import pygame
import os
import json
from typing import Dict, Optional, List
from enum import Enum
import threading
import time


class AudioType(Enum):
    """音效類型"""

    BGM = "bgm"  # 背景音樂
    SFX = "sfx"  # 音效
    VOICE = "voice"  # 語音
    AMBIENT = "ambient"  # 環境音


class AudioManager:
    """音效管理器"""

    def __init__(self):
        self.is_initialized = False

        # 音量設定
        self.master_volume = 1.0
        self.bgm_volume = 0.7
        self.sfx_volume = 0.8
        self.voice_volume = 0.9
        self.ambient_volume = 0.5

        # 音效資源
        self.bgm_tracks: Dict[str, pygame.mixer.Sound] = {}
        self.sfx_sounds: Dict[str, pygame.mixer.Sound] = {}
        self.voice_clips: Dict[str, pygame.mixer.Sound] = {}
        self.ambient_sounds: Dict[str, pygame.mixer.Sound] = {}

        # 播放狀態
        self.current_bgm = None
        self.current_bgm_name = None
        self.bgm_channel = None
        self.sfx_channels = []
        self.voice_channel = None
        self.ambient_channel = None

        # 淡入淡出控制
        self.fade_thread = None
        self.is_fading = False

        # 音效設定
        self.audio_config = {
            "bgm_folder": "assets/sounds/bgm",
            "sfx_folder": "assets/sounds/sfx",
            "voice_folder": "assets/sounds/voice",
            "ambient_folder": "assets/sounds/ambient",
            "supported_formats": [".mp3", ".ogg", ".wav"],
            "max_sfx_channels": 8,
        }

        # 初始化pygame音效
        self._initialize_audio()

    def _initialize_audio(self):
        """初始化音效系統"""
        try:
            # 檢查pygame是否已初始化
            if not pygame.get_init():
                pygame.init()

            # 初始化mixer
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()

            # 設置混音器通道數
            pygame.mixer.set_num_channels(16)

            # 獲取專用通道
            self.bgm_channel = pygame.mixer.Channel(0)
            self.voice_channel = pygame.mixer.Channel(1)
            self.ambient_channel = pygame.mixer.Channel(2)

            # SFX 使用多個通道
            self.sfx_channels = [
                pygame.mixer.Channel(i)
                for i in range(3, 3 + self.audio_config["max_sfx_channels"])
            ]

            self.is_initialized = True
            print("音效系統初始化成功")

            # 載入音效資源
            self._load_audio_resources()

        except Exception as e:
            print(f"音效系統初始化失敗: {e}")
            self.is_initialized = False

    def _load_audio_resources(self):
        """載入音效資源"""
        if not self.is_initialized:
            return

        # 載入BGM
        self._load_audio_folder(self.audio_config["bgm_folder"], self.bgm_tracks, "BGM")

        # 載入SFX
        self._load_audio_folder(self.audio_config["sfx_folder"], self.sfx_sounds, "SFX")

        # 載入語音
        self._load_audio_folder(
            self.audio_config["voice_folder"], self.voice_clips, "Voice"
        )

        # 載入環境音
        self._load_audio_folder(
            self.audio_config["ambient_folder"], self.ambient_sounds, "Ambient"
        )

    def _load_audio_folder(self, folder_path: str, audio_dict: Dict, audio_type: str):
        """載入指定資料夾中的音效"""
        if not os.path.exists(folder_path):
            print(f"{audio_type} 資料夾不存在: {folder_path}")
            return

        loaded_count = 0

        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # 檢查檔案格式
                if any(
                    filename.lower().endswith(fmt)
                    for fmt in self.audio_config["supported_formats"]
                ):
                    try:
                        # 載入音效
                        sound = pygame.mixer.Sound(file_path)

                        # 使用檔名（不含副檔名）作為鍵值
                        audio_name = os.path.splitext(filename)[0]
                        audio_dict[audio_name] = sound

                        loaded_count += 1

                    except Exception as e:
                        print(f"載入 {audio_type} 失敗 - {filename}: {e}")

            print(f"載入 {loaded_count} 個 {audio_type} 檔案")

        except Exception as e:
            print(f"讀取 {audio_type} 資料夾失敗: {e}")

    def play_bgm(self, bgm_name: str, loop: bool = True, fade_in: float = 0.0):
        """播放背景音樂"""
        if not self.is_initialized:
            print("音效系統未初始化，無法播放BGM")
            return False

        if bgm_name not in self.bgm_tracks:
            print(f"BGM不存在: {bgm_name}")
            return False

        try:
            # 停止當前BGM
            if self.current_bgm and self.bgm_channel.get_busy():
                if fade_in > 0:
                    self.fade_out_bgm(fade_in)
                else:
                    self.bgm_channel.stop()

            # 播放新BGM
            bgm_sound = self.bgm_tracks[bgm_name]
            loops = -1 if loop else 0

            if fade_in > 0:
                self.bgm_channel.play(
                    bgm_sound, loops=loops, fade_ms=int(fade_in * 1000)
                )
            else:
                self.bgm_channel.play(bgm_sound, loops=loops)

            # 設置音量
            self.bgm_channel.set_volume(self.bgm_volume * self.master_volume)

            self.current_bgm = bgm_sound
            self.current_bgm_name = bgm_name

            print(f"播放BGM: {bgm_name}")
            return True

        except Exception as e:
            print(f"播放BGM失敗: {e}")
            return False

    def stop_bgm(self, fade_out: float = 0.0):
        """停止背景音樂"""
        if not self.bgm_channel or not self.bgm_channel.get_busy():
            return

        try:
            if fade_out > 0:
                self.fade_out_bgm(fade_out)
            else:
                self.bgm_channel.stop()

            self.current_bgm = None
            self.current_bgm_name = None

        except Exception as e:
            print(f"停止BGM失敗: {e}")

    def pause_bgm(self):
        """暫停背景音樂"""
        if self.bgm_channel and self.bgm_channel.get_busy():
            self.bgm_channel.pause()

    def resume_bgm(self):
        """恢復背景音樂"""
        if self.bgm_channel:
            self.bgm_channel.unpause()

    def fade_out_bgm(self, fade_time: float):
        """淡出背景音樂"""
        if not self.bgm_channel or not self.bgm_channel.get_busy():
            return

        try:
            self.bgm_channel.fadeout(int(fade_time * 1000))
        except Exception as e:
            print(f"BGM淡出失敗: {e}")

    def play_sfx(self, sfx_name: str, volume: float = 1.0) -> bool:
        """播放音效"""
        if not self.is_initialized:
            return False

        if sfx_name not in self.sfx_sounds:
            print(f"音效不存在: {sfx_name}")
            return False

        try:
            # 找到可用的音效通道
            available_channel = None
            for channel in self.sfx_channels:
                if not channel.get_busy():
                    available_channel = channel
                    break

            if not available_channel:
                # 如果沒有可用通道，停止最老的音效
                available_channel = self.sfx_channels[0]
                available_channel.stop()

            # 播放音效
            sfx_sound = self.sfx_sounds[sfx_name]
            available_channel.play(sfx_sound)
            available_channel.set_volume(volume * self.sfx_volume * self.master_volume)

            return True

        except Exception as e:
            print(f"播放音效失敗: {e}")
            return False

    def play_voice(self, voice_name: str, volume: float = 1.0) -> bool:
        """播放語音"""
        if not self.is_initialized:
            return False

        if voice_name not in self.voice_clips:
            print(f"語音不存在: {voice_name}")
            return False

        try:
            # 停止當前語音
            if self.voice_channel and self.voice_channel.get_busy():
                self.voice_channel.stop()

            # 播放新語音
            voice_sound = self.voice_clips[voice_name]
            self.voice_channel.play(voice_sound)
            self.voice_channel.set_volume(
                volume * self.voice_volume * self.master_volume
            )

            return True

        except Exception as e:
            print(f"播放語音失敗: {e}")
            return False

    def play_ambient(
        self, ambient_name: str, loop: bool = True, volume: float = 1.0
    ) -> bool:
        """播放環境音"""
        if not self.is_initialized:
            return False

        if ambient_name not in self.ambient_sounds:
            print(f"環境音不存在: {ambient_name}")
            return False

        try:
            # 停止當前環境音
            if self.ambient_channel and self.ambient_channel.get_busy():
                self.ambient_channel.stop()

            # 播放新環境音
            ambient_sound = self.ambient_sounds[ambient_name]
            loops = -1 if loop else 0

            self.ambient_channel.play(ambient_sound, loops=loops)
            self.ambient_channel.set_volume(
                volume * self.ambient_volume * self.master_volume
            )

            return True

        except Exception as e:
            print(f"播放環境音失敗: {e}")
            return False

    def stop_ambient(self):
        """停止環境音"""
        if self.ambient_channel and self.ambient_channel.get_busy():
            self.ambient_channel.stop()

    def set_master_volume(self, volume: float):
        """設置主音量"""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()

    def set_bgm_volume(self, volume: float):
        """設置BGM音量"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.bgm_channel:
            self.bgm_channel.set_volume(self.bgm_volume * self.master_volume)

    def set_sfx_volume(self, volume: float):
        """設置音效音量"""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_voice_volume(self, volume: float):
        """設置語音音量"""
        self.voice_volume = max(0.0, min(1.0, volume))
        if self.voice_channel:
            self.voice_channel.set_volume(self.voice_volume * self.master_volume)

    def set_ambient_volume(self, volume: float):
        """設置環境音音量"""
        self.ambient_volume = max(0.0, min(1.0, volume))
        if self.ambient_channel:
            self.ambient_channel.set_volume(self.ambient_volume * self.master_volume)

    def _update_all_volumes(self):
        """更新所有音量"""
        if self.bgm_channel:
            self.bgm_channel.set_volume(self.bgm_volume * self.master_volume)
        if self.voice_channel:
            self.voice_channel.set_volume(self.voice_volume * self.master_volume)
        if self.ambient_channel:
            self.ambient_channel.set_volume(self.ambient_volume * self.master_volume)

    def get_volume_settings(self) -> Dict[str, float]:
        """獲取音量設定"""
        return {
            "master": self.master_volume,
            "bgm": self.bgm_volume,
            "sfx": self.sfx_volume,
            "voice": self.voice_volume,
            "ambient": self.ambient_volume,
        }

    def set_volume_settings(self, settings: Dict[str, float]):
        """設置音量設定"""
        if "master" in settings:
            self.set_master_volume(settings["master"])
        if "bgm" in settings:
            self.set_bgm_volume(settings["bgm"])
        if "sfx" in settings:
            self.set_sfx_volume(settings["sfx"])
        if "voice" in settings:
            self.set_voice_volume(settings["voice"])
        if "ambient" in settings:
            self.set_ambient_volume(settings["ambient"])

    def is_bgm_playing(self) -> bool:
        """檢查BGM是否正在播放"""
        return self.bgm_channel and self.bgm_channel.get_busy()

    def is_voice_playing(self) -> bool:
        """檢查語音是否正在播放"""
        return self.voice_channel and self.voice_channel.get_busy()

    def get_current_bgm(self) -> Optional[str]:
        """獲取當前播放的BGM名稱"""
        return self.current_bgm_name if self.is_bgm_playing() else None

    def get_available_audio(self) -> Dict[str, List[str]]:
        """獲取可用的音效列表"""
        return {
            "bgm": list(self.bgm_tracks.keys()),
            "sfx": list(self.sfx_sounds.keys()),
            "voice": list(self.voice_clips.keys()),
            "ambient": list(self.ambient_sounds.keys()),
        }

    def stop_all_audio(self):
        """停止所有音效"""
        try:
            pygame.mixer.stop()
            self.current_bgm = None
            self.current_bgm_name = None
        except Exception as e:
            print(f"停止所有音效失敗: {e}")

    def cleanup(self):
        """清理音效系統"""
        self.stop_all_audio()

        # 清理資源
        self.bgm_tracks.clear()
        self.sfx_sounds.clear()
        self.voice_clips.clear()
        self.ambient_sounds.clear()

        if self.is_initialized:
            try:
                pygame.mixer.quit()
            except:
                pass

        self.is_initialized = False
        print("音效系統已清理")


# 全域音效管理器實例
audio_manager = AudioManager()


# 便利函數
def play_bgm(bgm_name: str, loop: bool = True, fade_in: float = 0.0) -> bool:
    """播放背景音樂的便利函數"""
    return audio_manager.play_bgm(bgm_name, loop, fade_in)


def play_sfx(sfx_name: str, volume: float = 1.0) -> bool:
    """播放音效的便利函數"""
    return audio_manager.play_sfx(sfx_name, volume)


def play_voice(voice_name: str, volume: float = 1.0) -> bool:
    """播放語音的便利函數"""
    return audio_manager.play_voice(voice_name, volume)


def stop_bgm(fade_out: float = 0.0):
    """停止背景音樂的便利函數"""
    audio_manager.stop_bgm(fade_out)


def set_volume(audio_type: str, volume: float):
    """設置音量的便利函數"""
    if audio_type == "master":
        audio_manager.set_master_volume(volume)
    elif audio_type == "bgm":
        audio_manager.set_bgm_volume(volume)
    elif audio_type == "sfx":
        audio_manager.set_sfx_volume(volume)
    elif audio_type == "voice":
        audio_manager.set_voice_volume(volume)
    elif audio_type == "ambient":
        audio_manager.set_ambient_volume(volume)
