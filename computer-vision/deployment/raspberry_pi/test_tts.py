#!/usr/bin/env python3
"""Test script to verify text-to-speech is working."""

import subprocess

print("Testing macOS 'say' command for TTS...")

print("\n🔊 TESTING TEXT-TO-SPEECH")
print("=" * 60)
print("You should hear: 'Testing text to speech. Can you hear me?'")
print("=" * 60)

# Use macOS say command with Samantha voice at rate 175
subprocess.run(['say', '-v', 'Samantha', '-r', '175', "Testing text to speech. Can you hear me?"], check=True)

print("\n✅ TTS test completed!")
print("\nNow testing the fall detection message...")
print("=" * 60)

# Test the actual fall detection message
subprocess.run(['say', '-v', 'Samantha', '-r', '175', "A fall was detected. Are you okay? Please speak now if you are able to."], check=True)

print("\n✅ Fall alert test completed!")
print("=" * 60)
