import pefile, datetime, sys

pe = pefile.PE('BH3_Data/Native/UserAssembly.dll', fast_load=True)
print('Machine: 0x%X' % pe.FILE_HEADER.Machine)
ts = pe.FILE_HEADER.TimeDateStamp
print('TimeDateStamp:', ts, '->', datetime.datetime.utcfromtimestamp(ts))
print('SizeOfImage: 0x%X (%.1f MB)' % (pe.OPTIONAL_HEADER.SizeOfImage, pe.OPTIONAL_HEADER.SizeOfImage/1048576))
print('Sections:')
for s in pe.sections:
    name = s.Name.decode(errors='replace').rstrip('\x00')
    print('  %-8s VA=0x%08X VS=0x%08X (%7.1f MB) RS=0x%08X' %
          (name, s.VirtualAddress, s.Misc_VirtualSize, s.Misc_VirtualSize/1048576, s.SizeOfRawData))

# 入口点
print('EntryPoint: 0x%X' % pe.OPTIONAL_HEADER.AddressOfEntryPoint)
