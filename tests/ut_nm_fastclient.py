"""
Author: Justin Cappos
Description:
This test verifies the ResetVessel method works by first assidng several files to a vessel, resetting the vessel, and checking if the files and log were erased.

"""

from repyportability import *

add_dy_support(locals())

affix_stack = dy_import_module("affix_stack.r2py")
rsa = dy_import_module("rsa.r2py")
sha = dy_import_module("sha.r2py")


nodeman_file = openfile("nodeman.cfg", False)
nodeman_content = "mydict = " + nodeman_file.readat(10000, 0)
nodeman_file.close()

new_namespace = createvirtualnamespace(nodeman_content, "nodeman")
nodeman_dict = new_namespace.evaluate({})
mypubkey = rsa.rsa_publickey_to_string(nodeman_dict["mydict"]["publickey"]).replace(" ", "")

my_name = sha.sha_hexhash(mypubkey)
myaffix = affix_stack.AffixStack("(CoordinationAffix)(NamingAndResolverAffix)")



openconnection = myaffix.openconnection

time = dy_import_module("time.r2py")


import fastnmclient

if __name__ == '__main__':

  pubkey = {'e': 1515278400394037168869631887206225761783197636247636149274740854708478416229147500580877416652289990968676310353790883501744269103521055894342395180721167L, 'n': 8811850224687278929671477591179591903829730117649785862652866020803862826558480006479605958786097112503418194852731900367494958963787480076175614578652735061071079458992502737148356289391380249696938882025028801032667062564713111819847043202173425187133883586347323838509679062142786013585264788548556099117804213139295498187634341184917970175566549405203725955179602584979965820196023950630399933075080549044334508921319264315718790337460536601263126663173385674250739895046814277313031265034275415434440823182691254039184953842629364697394327806074576199279943114384828602178957150547925812518281418481896604655037L}
  time.time_updatetime(34612)
  nmhandle = fastnmclient.nmclient_createhandle(getmyip(), <nodemanager_port>)
  
  myhandleinfo = fastnmclient.nmclient_get_handle_info(nmhandle)

  myhandleinfo['publickey'] = pubkey

  myhandleinfo['privatekey'] = {'q': 54058458609373005761636236344701348569916976061233632302656354317296914836524068463339023907975088241991695932495814481647444694298985642399081803007236201209469946258941304883759055364999601996691930482382846773100579600645226048615117420700557109784424679718473031043919444221865548436936151591443700338637L, 'p': 163005946735584933080904947630005844643976533101833337498275325109161034533761907731163804211972028706576149578068245770343911608552263828770803393409524864116386113730846986186991705365903821748069417335817777744060812709585990055899981036005918570773920278122250955465866247822703170432353212868019982497201L, 'd': 2240169959722743128383109799584344927620631289695753164608137553948562513840905705755472646965204244185778446323692147882435315849145863268402636875283224769523136754021661455550898853194946272632624967823932300133454648259819576163836968537588009990175504497443778516954738281566994011669204200464480373455393955376955298830900816876217755539224711550233098080437180969137329334691279693903616444969433587901167778818088572448203744563568733073397445832643374417179790887207750843422586891294093361764515116975052446191135748633217162309228939861802346846701415099277659436864814394138247474263285983065177006045103L}

  fastnmclient.nmclient_set_handle_info(nmhandle, myhandleinfo)

  # get the vessel to use...
  myvessel = fastnmclient.nmclient_listaccessiblevessels(nmhandle,pubkey)[0][0]

  fastnmclient.nmclient_signedsay(nmhandle, "AddFileToVessel", myvessel, "hello","hellodata")
  fastnmclient.nmclient_signedsay(nmhandle, "AddFileToVessel", myvessel, "helloworld.r2py","log('hello world')\nwhile True: sleep(.1)")
  fastnmclient.nmclient_signedsay(nmhandle, "AddFileToVessel", myvessel, "hello2","hellodata")

  fastnmclient.nmclient_signedsay(nmhandle, "StartVesselEx", myvessel, "repyV2", "helloworld.r2py")
  

  # okay, now let's reset!
  fastnmclient.nmclient_signedsay(nmhandle, "ResetVessel", myvessel)

  
  filelist = fastnmclient.nmclient_signedsay(nmhandle, "ListFilesInVessel", myvessel)
  if filelist:
    raise Exception("Filelist is not empty after reset!")
  vessellog = fastnmclient.nmclient_signedsay(nmhandle, "ReadVesselLog", myvessel)
  if vessellog:
    raise Exception("Vessellog is not empty after reset!")
  fastnmclient.nmclient_signedsay(nmhandle, "AddFileToVessel", myvessel, "helloworld.r2py","log('hello world')\nwhile True: sleep(.1)")

  try:
    # this should succeed.   The previously started version should have been 
    # stopped by the reset.
    fastnmclient.nmclient_signedsay(nmhandle, "StartVesselEx", myvessel, "repyV2", "helloworld.r2py")
  finally:
    # always stop at the end...
    fastnmclient.nmclient_signedsay(nmhandle, "StopVessel", myvessel)


