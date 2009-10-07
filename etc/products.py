from msgpp_config import *

euro = "euro"
euro4 = "euro4"
eurol = "eurol"
eurotv = "eurotv"
eurotv4n = "eurotv4n"

scan = "scan"
scan2 = "scan2"

mesanX = "mesanX"

globe = "globe"

s_euro = euro.ljust(8,"_")
s_euro4 = euro4.ljust(8,"_")
s_eurol = eurol.ljust(8,"_")
s_eurotv = eurotv.ljust(8,"_")
s_eurotv4n = eurotv4n.ljust(8,"_")

s_scan = scan.ljust(8,"_")
s_scan2 = scan2.ljust(8,"_")

s_mesanX = mesanX.ljust(8,"_")

s_globe = globe.ljust(8,"_")

PRODUCTS = {"globe":

                {"PGE02d":[(LOCAL_SIR_DIR+"/msg_02d_"+s_globe+"%y%m%d%H%M.tif",
                            SIR_DIR+"/msg_02d_"+s_globe+"%y%m%d%H%M.tif_original"),
                           (LOCAL_SIR_DIR+"/msg_02dp"+s_globe+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02dp"+s_globe+"%y%m%d%H%M.png_original")],
            
                 "overview":[(LOCAL_SIR_DIR+"/msg_ovw_"+s_globe+"%y%m%d%H%M.tif",
                              SIR_DIR+"/msg_ovw_"+s_globe+"%y%m%d%H%M.tif_original"),
                             (LOCAL_SIR_DIR+"/msg_ovwp"+s_globe+"%y%m%d%H%M.png",
                              SIR_DIR+"/msg_ovwp"+s_globe+"%y%m%d%H%M.png_original"),
                             RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+globe+"_rgb_overview.png"]},
            
            "euro4":
                {"PGE02":[(LOCAL_SIR_DIR+"/msg_02a_"+s_euro4+"%y%m%d%H%M.tif",
                           SIR_DIR+"/msg_02a_"+s_euro4+"%y%m%d%H%M.tif_original")],
                 
                 "PGE02b":[(LOCAL_SIR_DIR+"/msg_02bp"+s_euro4+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02bp"+s_euro4+"%y%m%d%H%M.png_original"),
                           (LOCAL_SIR_DIR+"/msg_02bj"+s_euro4+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02bj"+s_euro4+"%y%m%d%H%M.png_original")],
                 
                 "PGE02c":[(LOCAL_SIR_DIR+"/msg_02cp"+s_euro4+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02cp"+s_euro4+"%y%m%d%H%M.png_original")],
                 
                 "PGE02d":[(LOCAL_SIR_DIR+"/msg_02d_"+s_euro4+"%y%m%d%H%M.tif",
                            SIR_DIR+"/msg_02d_"+s_euro4+"%y%m%d%H%M.tif_original"),
                           (LOCAL_SIR_DIR+"/msg_02dp"+s_euro4+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02dp"+s_euro4+"%y%m%d%H%M.png_original")],

                 "PGE02e":[(LOCAL_SIR_DIR+"/msg_02e_"+s_euro4+"%y%m%d%H%M.tif",
                            SIR_DIR+"/msg_02e_"+s_euro4+"%y%m%d%H%M.tif_original"),
                           (LOCAL_SIR_DIR+"/msg_02ep"+s_euro4+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02ep"+s_euro4+"%y%m%d%H%M.png_original")],

                 "PGE03":[(LOCAL_SIR_DIR+"/msg_03a_"+s_euro4+"%y%m%d%H%M.tif",
                           SIR_DIR+"/msg_03a_"+s_euro4+"%y%m%d%H%M.tif_original"),
                          (LOCAL_SIR_DIR+"/msg_03ap"+s_euro4+"%y%m%d%H%M.png",
                           SIR_DIR+"/msg_03ap"+s_euro4+"%y%m%d%H%M.png_original")],

                 "ir9":[(LOCAL_SIR_DIR+"/msg_ir9_"+s_euro4+"%y%m%d%H%M.tif",
                         SIR_DIR+"/msg_ir9_"+s_euro4+"%y%m%d%H%M.tif_original"),
                        (LOCAL_SIR_DIR+"/msg_ir9p"+s_euro4+"%y%m%d%H%M.png",
                         SIR_DIR+"/msg_ir9p"+s_euro4+"%y%m%d%H%M.png_original"),
                        RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_bw_ch9.png"],

                 "airmass":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_airmass.png"],

                 "wv_high":[(LOCAL_SIR_DIR+"/msg_ir5_"+s_euro4+"%y%m%d%H%M.tif",
                             SIR_DIR+"/msg_ir5_"+s_euro4+"%y%m%d%H%M.tif_original"),
                            RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_bw_ch5.png"],

                 "wv_low":[(LOCAL_SIR_DIR+"/msg_ir6_"+s_euro4+"%y%m%d%H%M.tif",
                            SIR_DIR+"/msg_ir6_"+s_euro4+"%y%m%d%H%M.tif_original"),
                           RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_bw_ch6.png"],
                 
                 "overview":[(LOCAL_SIR_DIR+"/msg_ovw_"+s_euro4+"%y%m%d%H%M.tif",
                              SIR_DIR+"/msg_ovw_"+s_euro4+"%y%m%d%H%M.tif_original"),
                             (LOCAL_SIR_DIR+"/msg_ovwp"+s_euro4+"%y%m%d%H%M.png",
                              SIR_DIR+"/msg_ovwp"+s_euro4+"%y%m%d%H%M.png_original"),
                             RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_overview.png"],
                 
                 "hr_overview":[(LOCAL_SIR_DIR+"/msg_hovw"+s_euro4+"%y%m%d%H%M.tif",
                                 SIR_DIR+"/msg_hovw"+s_euro4+"%y%m%d%H%M.tif_original"),
                                (LOCAL_SIR_DIR+"/msg_hovp"+s_euro4+"%y%m%d%H%M.png",
                                 SIR_DIR+"/msg_hovp"+s_euro4+"%y%m%d%H%M.png_original"),
                                RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_hr_overview.png"],
                 
                 "cloudtop":[(LOCAL_SIR_DIR+"/msg_clt_"+s_euro4+"%y%m%d%H%M.tif",
                              SIR_DIR+"/msg_clt_"+s_euro4+"%y%m%d%H%M.tif_original"),
                             (LOCAL_SIR_DIR+"/msg_cltp"+s_euro4+"%y%m%d%H%M.png",
                              SIR_DIR+"/msg_cltp"+s_euro4+"%y%m%d%H%M.png_original"),
                             RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_cloudtop_co2corr.png"],

                 "nightfog":[(LOCAL_SIR_DIR+"/msg_nfog"+s_euro4+"%y%m%d%H%M.tif",
                              SIR_DIR+"/msg_nfog"+s_euro4+"%y%m%d%H%M.tif_original"),
                             (LOCAL_SIR_DIR+"/msg_nfop"+s_euro4+"%y%m%d%H%M.png",
                              SIR_DIR+"/msg_nfop"+s_euro4+"%y%m%d%H%M.png_original"),
                             RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_nightfog.png"],

                 "fog":[(LOCAL_SIR_DIR+"/msg_fog_"+s_euro4+"%y%m%d%H%M.tif",
                         SIR_DIR+"/msg_fog_"+s_euro4+"%y%m%d%H%M.tif_original"),
                        (LOCAL_SIR_DIR+"/msg_fogp"+s_euro4+"%y%m%d%H%M.png",
                         SIR_DIR+"/msg_fogp"+s_euro4+"%y%m%d%H%M.png_original"),
                        RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_fog.png"],

                 "convection":[(LOCAL_SIR_DIR+"/msg_conv"+s_euro4+"%y%m%d%H%M.tif",
                                SIR_DIR+"/msg_conv"+s_euro4+"%y%m%d%H%M.tif_original"),
                               (LOCAL_SIR_DIR+"/msg_conp"+s_euro4+"%y%m%d%H%M.png",
                                SIR_DIR+"/msg_conp"+s_euro4+"%y%m%d%H%M.png_original"),
                               RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_severe_convection.png"],
             
                 "greensnow":[(LOCAL_SIR_DIR+"/msg_snow"+s_euro4+"%y%m%d%H%M.tif",
                               SIR_DIR+"/msg_snow"+s_euro4+"%y%m%d%H%M.tif_original"),
                              (LOCAL_SIR_DIR+"/msg_snop"+s_euro4+"%y%m%d%H%M.png",
                               SIR_DIR+"/msg_snop"+s_euro4+"%y%m%d%H%M.png_original"),
                              RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+euro4+"_rgb_greensnow.png"]},
            
            "eurol":
                {"ir9":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_bw_ch9.png"],

                 "airmass":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_airmass.png"],

                 "wv_high":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_bw_ch5.png"],

                 "wv_low":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_bw_ch6.png"],
                 
                 "overview":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_overview.png"],
                 
                 "hr_overview":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_hr_overview.png"],
                 
                 "cloudtop":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_cloudtop_co2corr.png"],

                 "nightfog":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_nightfog.png"],

                 "fog":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_fog.png"],

                 "convection":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_severe_convection.png"],
             
                 "greensnow":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurol+"_rgb_greensnow.png"]},
            
            "eurotv":
                {"PGE02c":[(LOCAL_SIR_DIR+"/msg_02cp"+s_eurotv+"%y%m%d%H%M.png",
                            SIR_DIR+"/msg_02cp"+s_eurotv+"%y%m%d%H%M.png_original")],

                 "overview":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurotv+"_rgb_overview.png"],

                 "fog":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurotv+"_rgb_fog.png"],

                 "greensnow":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+eurotv+"_rgb_greensnow.png"]},
                 
            "euro":
                {"PGE02c":[(LOCAL_SIR_DIR+"/meteoict"+s_euro+"%y%m%d%H%M.tif",
                            SIR_DIR+"/meteoict"+s_euro+"%y%m%d%H%M.tif_original"),
                           (LOCAL_SIR_DIR+"/meteircj"+s_euro+"%y%m%d%H%M.jpg",
                            SIR_DIR+"/meteircj"+s_euro+"%y%m%d%H%M.jpg_original"),
                           (LOCAL_SIR_DIR+"/metirccj"+s_euro+"%y%m%d%H%M.jpg",
                            SIR_DIR+"/metirccj"+s_euro+"%y%m%d%H%M.jpg_original")]},
            
            "scan":
                {"PGE02b":[(LOCAL_SIR_DIR+"/msg_02bj"+s_scan+"%y%m%d%H%M.jpg",
                            SIR_DIR+"/msg_02bj"+s_scan+"%y%m%d%H%M.jpg_original")],
                 
                 "PGE02c":[(LOCAL_SIR_DIR+"/meteirct"+s_scan+"%y%m%d%H%M.tif",
                            SIR_DIR+"/meteirct"+s_scan+"%y%m%d%H%M.tif_original"),
                           (LOCAL_SIR_DIR+"/meteircj"+s_scan+"%y%m%d%H%M.jpg",
                            SIR_DIR+"/meteircj"+s_scan+"%y%m%d%H%M.jpg_original"),
                           (LOCAL_SIR_DIR+"/metirccj"+s_scan+"%y%m%d%H%M.jpg",
                            SIR_DIR+"/metirccj"+s_scan+"%y%m%d%H%M.jpg_original")]},
                
            "scan2":
                {"PGE03":[(LOCAL_SIR_DIR+"/msg_03ap"+s_scan2+"%y%m%d%H%M.png",
                           SIR_DIR+"/msg_03ap"+s_scan2+"%y%m%d%H%M.png_original")],
                
                 "cloudtop":[(LOCAL_SIR_DIR+"/msg_cltp"+s_scan2+"%y%m%d%H%M.png",
                              SIR_DIR+"/msg_cltp"+s_scan2+"%y%m%d%H%M.png_original"),
                             RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+scan2+"_rgb_cloudtop_co2corr.png"],
                 

                 "convection":[(LOCAL_SIR_DIR+"/msgconvp"+s_scan2+"%y%m%d%H%M.png",
                                SIR_DIR+"/msgconvp"+s_scan2+"%y%m%d%H%M.png_original"),
                               RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+scan2+"_rgb_severe_convection.png"],
                 

                 "greensnow":[(LOCAL_SIR_DIR+"/msgsnowp"+s_scan2+"%y%m%d%H%M.png",
                               SIR_DIR+"/msgsnowp"+s_scan2+"%y%m%d%H%M.png_original"),
                              RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+scan2+"_rgb_greensnow.png"]},

            "mesanX":
                {"overview":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+mesanX+"_rgb_overview.png"],
                 
                 "fog":[RGBDIR_OUT+"/"+MSG_SATELLITE+"_%Y%m%d%H%M_"+mesanX+"_rgb_fog.png"]},
            
            "eurotv4n":
                {"PGE02b":[(LOCAL_SIR_DIR+"/msg_02d_"+s_eurotv4n+"%y%m%d%H%M.tif",
                            SIR_DIR+"/msg_02d_"+s_eurotv4n+"%y%m%d%H%M.tif_original")]}


            }
