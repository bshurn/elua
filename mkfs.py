# A script to convert an entire directory to a C array, in the "romfs" format
import os, sys
import re
import struct

_crtline = '  '
_numdata = 0
_bytecnt = 0

maxlen = 30

# Line output function
def _add_data( data, outfile, moredata = True ):
  global _crtline, _numdata, _bytecnt
  _bytecnt = _bytecnt + 1
  if moredata:
    _crtline = _crtline + "0x%02X, " % data
  else:
    _crtline = _crtline + "0x%02X" % data    
  _numdata = _numdata + 1
  if _numdata == 16 or not moredata:
    outfile.write( _crtline + '\n' )
    _crtline = '  '
    _numdata = 0

# dirname - the directory where the files are located.
# outname - the name of the C output
# flist - list of files
# mode - preprocess the file system:
#   "verbatim" - copy the files directly to the FS as they are
#   "compile" - precompile all files to Lua bytecode and then copy them
#   "compress" - keep the source code, but compress it with LuaSrcDiet
# compcmd - the command to use for compiling if "mode" is "compile"
# Returns True for OK, False for error
def mkfs( dirname, outname, flist, mode, compcmd ):
  # Try to create the output files
  outfname = outname + ".h"
  try:
    outfile = file( outfname, "wb" )
  except:
    print "Unable to create output file"
    return False
  
  global _crtline, _numdata, _bytecnt
  _crtline = '  '
  _numdata = 0
  _bytecnt = 0
  # Generate headers
  outfile.write( "// Generated by mkfs.py\n// DO NOT MODIFY\n\n" )
  outfile.write( "#ifndef __%s_H__\n#define __%s_H__\n\n" % ( outname.upper(), outname.upper() ) )
  
  outfile.write( "const unsigned char %s_fs[] = \n{\n" % ( outname.lower() ) )
  
  # Process all files
  for fname in flist:
    if len( fname ) > maxlen:
      print "Skipping %s (name longer than %d chars)" % ( fname, maxlen )
      continue 
      
    # Get actual file name
    realname = os.path.join( dirname, fname )
    
    # Ensure it actually is a file
    if not os.path.isfile( realname ):
      print "Skipping %s ... (not found or not a regular file)" % fname
      continue
      
    # Try to open and read the file
    try:
      crtfile = file( realname, "rb" )
    except:
      outfile.close()
      os.remove( outfname )
      print "Unable to read %s" % fname    
      return False
    
    # Do we need to process the file?
    fextpart = ''
    if mode == "compile" or mode == "compress":
      fnamepart, fextpart = os.path.splitext( realname )
      if mode == "compress":
        newext = ".lua.tmp"
      else:
        newext = ".lc"
      if fextpart == ".lua":
        newname = fnamepart + newext
        if mode == "compress":
          print "Compressing %s to %s ..." % ( realname, newname )
        else:
          print "Cross compiling %s to %s ..." % ( realname, newname )
        os.system( compcmd % ( newname, realname ) )
        # TODO: this assumes that the cross compiler ended OK
        crtfile.close()
        try:
          crtfile = file( newname, "rb" )
        except:
          outfile.close()
          os.remove( outfname )
          print "Unable to read %s" % newname
          return False
        if mode == "compile":
          fnamepart, fextpart = os.path.splitext( fname )
          fname = fnamepart + ".lc"
    filedata = crtfile.read()
    crtfile.close()
    if fextpart == ".lua" and mode != "verbatim":
      os.remove( newname )

    # Write name, size, id, numpars
    for c in fname:
      _add_data( ord( c ), outfile )
    _add_data( 0, outfile ) # ASCIIZ
    size_l = len( filedata ) & 0xFF
    size_h = ( len( filedata ) >> 8 ) & 0xFF
    _add_data( size_l, outfile )
    _add_data( size_h, outfile )
    # Round to a multiple of 4
    actual = len( filedata )
    while _bytecnt & 4 != 0:
      _add_data( 0, outfile )
      actual = actual + 1
    # Then write the rest of the file
    for c in filedata:
      _add_data( ord( c ), outfile )
    
    # Report
    print "Encoded file %s (%d bytes real size, %d bytes after rounding)" % ( fname, len( filedata ), actual )
    
  # All done, write the final "0" (terminator)
  _add_data( 0, outfile, False )
  outfile.write( "};\n\n#endif\n" );
  outfile.close()
  print "Done, total size is %d bytes" % _bytecnt
  return True

