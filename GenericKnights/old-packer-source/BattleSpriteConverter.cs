using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;

internal static class BattleSpriteConverter
{
	private const int Width = 256;

	private const int Height = 488;

	private const int PaletteBytes = 512;

	private const int RawPixelBytes = 36864;

	private const int RawPixelCount = 73728;

	public static void ConvertBmpToSpr(string bmpPath, string outputPath, bool portraitInMiddle = false)
	{
		byte[] array = File.ReadAllBytes(bmpPath);
		if (array.Length < 54 || array[0] != 66 || array[1] != 77)
		{
			throw new InvalidDataException("Sprite BMP invalido: " + bmpPath);
		}
		int num = ReadInt32(array, 10);
		int num2 = ReadInt32(array, 14);
		int num3 = ReadInt32(array, 18);
		int num4 = ReadInt32(array, 22);
		ushort num5 = ReadUInt16(array, 26);
		ushort num6 = ReadUInt16(array, 28);
		uint num7 = ReadUInt32(array, 30);
		if (num2 < 40 || num3 != 256 || Math.Abs(num4) != 488 || num5 != 1 || num6 != 8 || num7 != 0)
		{
			throw new InvalidDataException($"{Path.GetFileName(bmpPath)} deve ser BMP indexado 8-bpp, {256}x{488}, sem compressao.");
		}
		int num8 = 14 + num2;
		if (num8 < 0 || num8 + 1024 > array.Length)
		{
			throw new InvalidDataException("Paleta BMP de 256 cores incompleta.");
		}
		int num9 = (256 * num6 + 31) / 32 * 4;
		if (num < 0 || num + num9 * 488 > array.Length)
		{
			throw new InvalidDataException("Dados de pixels BMP incompletos.");
		}
		byte[] array2 = new byte[124928];
		bool flag = num4 > 0;
		byte b = 0;
		for (int i = 0; i < 488; i++)
		{
			int num10 = (flag ? (487 - i) : i);
			int start = num + num10 * num9;
			array.AsSpan(start, 256).CopyTo(array2.AsSpan(i * 256, 256));
			Span<byte> span = array2.AsSpan(i * 256, 256);
			for (int j = 0; j < span.Length; j++)
			{
				byte val = (byte)(span[j] & 0x0F);
				span[j] = val;
				b = Math.Max(b, val);
			}
		}
		if (b > 15)
		{
			throw new InvalidDataException($"{Path.GetFileName(bmpPath)} usa indice de cor {b}; " + "sprites FFT aceitam somente indices 0..15 por paleta.");
		}
		byte[] array3 = new byte[array2.Length];
		if (portraitInMiddle)
		{
			// PSX sheets already use the native SPR order: 256 body rows,
			// 32 portrait rows, then 200 additional body rows.
			array2.CopyTo(array3, 0);
		}
		else
		{
			// WotL/editor sheets move the portrait to the final 32 rows.
			array2.AsSpan(0, 65536).CopyTo(array3);
			array2.AsSpan(116736, 8192).CopyTo(array3.AsSpan(65536));
			array2.AsSpan(65536, 51200).CopyTo(array3.AsSpan(73728));
		}
		List<byte> list = new List<byte>(48000);
		for (int k = 0; k < 256; k++)
		{
			int num11 = num8 + k * 4;
			byte b2 = array[num11];
			byte b3 = array[num11 + 1];
			byte b4 = array[num11 + 2];
			ushort num12 = (ushort)((b4 >> 3) | (b3 >> 3 << 5) | (b2 >> 3 << 10));
			if (k % 16 == 0 && b4 == 0 && b3 == 0 && b2 == 0)
			{
				num12 = 0;
			}
			list.Add((byte)num12);
			list.Add((byte)(num12 >> 8));
		}
		if (list.Count != 512)
		{
			throw new InvalidOperationException("Falha interna ao gerar paletas SPR.");
		}
		for (int l = 0; l < 73728; l += 2)
		{
			list.Add((byte)(array3[l] | (array3[l + 1] << 4)));
		}
		list.AddRange(CompressRle(array3.AsSpan(73728)));
		Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outputPath))!);
		File.WriteAllBytes(outputPath, list.ToArray());
		if (!DecodePixels(list.ToArray()).AsSpan().SequenceEqual(array3))
		{
			throw new InvalidDataException("A verificacao BMP -> SPR -> pixels falhou.");
		}
		Console.WriteLine($"[FFTModPacker:Sprite] {Path.GetFileName(bmpPath)} -> {Path.GetFileName(outputPath)} | {list.Count} bytes | indice max={b} | round-trip OK");
	}

	private static byte[] CompressRle(ReadOnlySpan<byte> pixels)
	{
		byte[] array = new byte[pixels.Length];
		for (int i = 0; i < pixels.Length; i += 2)
		{
			array[i] = pixels[i + 1];
			array[i + 1] = pixels[i];
		}
		List<byte> list = new List<byte>(pixels.Length / 2);
		int num = 0;
		while (num < array.Length)
		{
			int j;
			for (j = 0; num + j < array.Length && array[num + j] == 0 && j < 4095; j++)
			{
			}
			if (j == 0)
			{
				list.Add(array[num++]);
			}
			else if (j < 16)
			{
				list.Add(0);
				if ((uint)(j - 7) <= 1u)
				{
					list.Add(0);
				}
				list.Add((byte)j);
				num += j;
			}
			else if (j < 256)
			{
				list.Add(0);
				list.Add(7);
				list.Add((byte)(j & 0xF));
				list.Add((byte)((j >> 4) & 0xF));
				num += j;
			}
			else
			{
				list.Add(0);
				list.Add(8);
				list.Add((byte)(j & 0xF));
				list.Add((byte)((j >> 4) & 0xF));
				list.Add((byte)((j >> 8) & 0xF));
				num += j;
			}
		}
		byte[] array2 = new byte[(list.Count + 1) / 2];
		for (int k = 0; k < list.Count; k += 2)
		{
			array2[k / 2] = (byte)(list[k] << 4);
			if (k + 1 < list.Count)
			{
				array2[k / 2] |= list[k + 1];
			}
		}
		return array2;
	}

	private static byte[] DecodePixels(byte[] spr)
	{
		List<byte> list = new List<byte>(124928);
		for (int i = 512; i < 37376; i++)
		{
			list.Add((byte)(spr[i] & 0xF));
			list.Add((byte)(spr[i] >> 4));
		}
		byte[] array = new byte[(spr.Length - 512 - 36864) * 2];
		for (int j = 37376; j < spr.Length; j++)
		{
			int num = (j - 512 - 36864) * 2;
			array[num] = (byte)(spr[j] >> 4);
			array[num + 1] = (byte)(spr[j] & 0xF);
		}
		List<byte> list2 = new List<byte>(51200);
		int num2 = 0;
		while (num2 < array.Length && list2.Count < 51200)
		{
			byte b = array[num2++];
			if (b != 0)
			{
				list2.Add(b);
				continue;
			}
			if (num2 >= array.Length)
			{
				break;
			}
			int num3 = array[num2++];
			if (num3 == 7 && num2 + 1 < array.Length)
			{
				num3 = array[num2++] | (array[num2++] << 4);
			}
			else if (num3 == 8 && num2 + 2 < array.Length)
			{
				num3 = array[num2++] | (array[num2++] << 4) | (array[num2++] << 8);
			}
			else if (num3 == 0 && num2 < array.Length)
			{
				num3 = array[num2++];
			}
			for (int k = 0; k < num3; k++)
			{
				if (list2.Count >= 51200)
				{
					break;
				}
				list2.Add(0);
			}
		}
		for (int l = 0; l + 1 < list2.Count; l += 2)
		{
			List<byte> list3 = list2;
			int index = l;
			int index2 = l + 1;
			byte value = list2[l + 1];
			byte value2 = list2[l];
			list3[index] = value;
			list2[index2] = value2;
		}
		list.AddRange(list2);
		if (list.Count != 124928)
		{
			throw new InvalidDataException($"SPR decodificou {list.Count} pixels; esperado {124928}.");
		}
		return list.ToArray();
	}

	private static int ReadInt32(byte[] bytes, int offset)
	{
		return BinaryPrimitives.ReadInt32LittleEndian(bytes.AsSpan(offset, 4));
	}

	private static uint ReadUInt32(byte[] bytes, int offset)
	{
		return BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(offset, 4));
	}

	private static ushort ReadUInt16(byte[] bytes, int offset)
	{
		return BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(offset, 2));
	}
}
