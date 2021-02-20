# requires pykep PR branch for 
# https://github.com/esa/pykep/pull/127

# plots results of good sequences determined by solarorbitermulti.py,

from math import acos
import time

from numpy import sign
from numpy.linalg import norm
from pykep import AU, epoch
from pykep.planet import jpl_lp
from pykep.trajopt.gym._solar_orbiter import _solar_orbiter_udp
import unittest as _ut

import matplotlib.pyplot as plt
import pygmo as pg

# Other imports
tmin = epoch(time.time() / (24*3600) - 30*365 -7 + 2/24 - 2*365)
tmax = epoch(time.time() / (24*3600) - 30*365 -7 + 2/24 + 2*365)

def names(seq):
    return " ".join((p.name) for p in seq)

class gym_test_case(_ut.TestCase):
    """Test case for the gym
    """

    def runTest(self):
        self.run_solar_orbiter_test()
        
    def run_solar_orbiter_test(self):
        from pykep.trajopt import gym
        udp = gym.solar_orbiter
        x = [7.52574686e+03, 5.89460811e+02, 3.04820667e+02, 4.90095761e+02,
        4.41678580e+02, 5.59871619e+02, 5.39100020e+02, 4.49401876e+02,
        2.24700938e+02, 1.60267063e+00, 1.39925808e+00]
        old_fitness = udp.fitness(x)
        self.assertAlmostEqual(old_fitness[0], 1.7918120371867503)
    
        udp_rev = gym.solar_orbiter_evolve_rev
        indices = [1, 1, 1, 1, 4, 3, 4, 2]
        new_fitness = udp_rev.fitness(x[:-2]+indices+x[-2:])
        self.assertAlmostEqual(new_fitness[0], 1.7918120371867503)
        self.assertEqual(new_fitness, old_fitness)

earth = jpl_lp("earth")
venus = jpl_lp("venus")

results = [
    [ 1.5799430791765368, [earth, venus, venus, earth, venus, venus, earth, venus], [7459.829458661072, 139.48789397550001, 407.0783891770967, 630.9462361245469, 71.34045907501172, 388.64641725461433, 233.4309610696611, 141.05425726994247, 2.433184698261979, 1.05783212161269] ],
    [ 1.582758867915829, [earth, venus, venus, earth, venus, venus, venus, earth, venus], [7338.85486129454, 220.30538683970377, 420.3194737456401, 67.62244842224129, 371.8673271285525, 671.6761619194273, 674.1004349280787, 46.015593785250815, 195.2517707382238, -5.4017810717711106, 1.0578321216589621] ],
    [ 1.5827855926615872, [earth, venus, venus, earth, earth, venus, venus, venus, earth, venus], [7364.16507373526, 211.7480881006781, 411.9902431401058, 56.589051658298125, 577.8420931100343, 57.939288241916046, 410.36455767031646, 674.1001712577988, 46.02303212465827, 195.2497102873121, 0.8887045055292584, 1.057832121612691] ],
    [ 1.5869406337191556, [earth, venus, venus, earth, venus, venus, venus, venus, earth, venus], [7936.549505222622, 203.45154140369212, 432.4257637531694, 65.25020033681295, 382.7438620039275, 431.58266380712143, 431.6015009740182, 431.614951925279, 74.68613968995557, 196.37644338907242, 2.3756761879452366, 1.057832121612691] ],
    [ 1.5918749372642802, [earth, venus, venus, earth, venus, earth, venus, venus, earth, venus], [7358.136194615376, 218.55397458251986, 405.6101336673417, 58.34805115448539, 351.3135968631085, 899.2695530165631, 86.91945688668248, 343.4674819484209, 285.3544484798128, 99.18544234291716, 3.249721758021216, 1.0580833059354895] ],
    [ 1.5971213000604243, [earth, venus, earth, venus, venus, venus, venus, earth, venus], [7756.062884379299, 247.40269481367864, 54.601721805121045, 392.31561805618037, 434.64311180913927, 434.6299456890198, 434.62111690943516, 54.959226707129424, 194.4768363013252, -5.377643102505771, 1.057832121612691] ],
    [ 1.599736196067762, [earth, venus, venus, venus, venus, venus, earth, venus], [7885.2122642154145, 237.81429206565917, 410.79875073491974, 672.2567946450677, 672.2505075243745, 410.8652737474202, 91.20607633070173, 198.6886499034353, 2.313039260891076, 1.057832121612691] ],
    [ 1.6172195720535436, [earth, earth, venus, venus, venus, venus, venus, venus, earth, venus], [7354.973545725112, 671.6123868743731, 108.51031173470275, 441.9805767565839, 441.98570184876644, 441.99019551305446, 441.99491598751496, 441.99862493190784, 63.80020208653165, 182.41242496374997, 2.345522121076185, 1.057832121612691] ],
    [ 1.6231882167906573, [earth, earth, venus, venus, venus, venus, venus, earth, venus], [7941.086109799286, 663.7844408414803, 111.08746040334651, 410.691265945796, 673.0972096489628, 673.0954861825986, 410.59921504339974, 77.18837024910968, 203.68111123635106, -5.553846489700374, 1.057832121612691] ],
    [ 1.641424770794312, [earth, earth, venus, venus, venus, venus, earth, venus], [7914.27096283868, 683.4991184267739, 112.41993851685407, 427.83780229385235, 427.81107979588006, 427.7844274251649, 409.34682859937413, 107.54544093206883, 1.2527988521915003, 1.05783212161269] ],
    [ 1.657645725198372, [earth, earth, earth, venus, venus, earth, venus], [7224.650857857882, 686.1144767095738, 685.9850262742117, 109.91258711302176, 449.3548345519095, 71.92150898982119, 192.4881549112052, -4.238224559903115, 1.0578343952197233] ],
    [ 1.677828985811071, [earth, venus, venus, earth, venus, earth, venus], [7363.59904503077, 223.61097968931222, 391.5812788508969, 54.92383829808823, 598.7773268680944, 685.6411687948735, 94.04628594591799, 0.94979717156665, 1.05783212161269] ],
    [ 1.6864261259205846, [earth, earth, venus, venus, earth, venus, venus, earth, venus, venus], [7941.812819685203, 662.9624900216329, 101.75645625493065, 434.38004744001717, 140.14034011539778, 149.4668063372269, 371.5965040529503, 690.3468737711753, 93.39539195237836, 336.96247878531165, -3.949672977372596, 1.0578577305196428] ],
    [ 1.687853188012749, [earth, venus, venus, venus, venus, earth, venus], [7412.5639424031615, 165.42955907267108, 430.68175756369885, 430.6601148633638, 430.63998954590414, 428.93506292378436, 110.42190318617956, -5.310690656530455, 1.05783212161269] ],
    [ 1.6880498240452984, [earth, venus, venus, earth, venus, earth, venus, venus], [7354.186780134925, 224.49591073159797, 398.21981216950064, 626.5694909388403, 31.243488917932044, 698.5476715226133, 88.83672231105145, 328.74663272355576, 0.9181920049912096, 1.05783212161269] ],
    [ 1.6883069664756682, [earth, venus, earth, venus, venus, earth, venus], [7759.318863424436, 244.96979088322973, 53.7457996450254, 380.4892554256127, 430.728118092195, 428.54658537914844, 110.3472501162992, -5.323792785400807, 1.05783212161269] ],
    [ 1.6929774350714137, [earth, venus, earth, earth, venus, venus, earth, earth, venus], [7745.732462391677, 280.17005792218424, 160.44925691634623, 365.2553592758319, 193.33067812712983, 421.49484068514937, 56.23676866667671, 594.6856008367524, 95.58540245532303, -4.367019354379117, 1.05783212161269] ],
    [ 1.6955921686650495, [earth, venus, venus, earth, venus, venus, earth, earth, venus], [7951.380182150303, 215.05027824454052, 400.706938197528, 56.26398887594333, 638.9634233258095, 391.30336956907894, 214.542589900062, 365.25597885907, 174.70934718795434, 1.4355949005588813, 1.057832121612691] ],
    [ 1.7041671398266378, [earth, earth, earth, venus, venus, earth, earth, venus], [7219.114469626816, 688.5475920368789, 688.4350600707288, 112.07910744588881, 449.39904541084525, 68.50501898244791, 617.0392715557612, 111.39786637675968, -4.12947602302374, 1.0578321216793996] ],
    [ 1.704167385542747, [earth, earth, venus, venus, earth, earth, venus], [7908.886980331182, 687.5292404082522, 111.75792546480947, 449.3990457148285, 68.50649629822546, 617.0396447588922, 111.39797325105393, 2.153705972710661, 1.05783212161269] ],
    [ 1.704354952148091, [earth, venus, venus, earth, earth, venus, venus, earth, earth, venus], [7247.759912464416, 252.98331385410268, 447.65315862629546, 198.42377161210274, 365.25578738304375, 209.06694592071068, 434.8738330308033, 69.606360446048, 617.320190685222, 111.4779093761153, -4.129995010369011, 1.057832121612691] ],
    [ 1.7256850629183578, [earth, earth, venus, earth, venus, venus, earth, venus, venus], [7004.401479421331, 730.5124059716762, 271.1930729307303, 74.01085764974744, 171.94203087218924, 375.6024007265941, 682.5068056015407, 93.39467257530711, 341.27485827255464, 0.92094755111545, 1.05783212161269] ],
    [ 1.7324677410984837, [earth, venus, venus, earth, venus, venus, earth, venus, venus], [7399.635727597496, 168.93959455849864, 444.67323387525613, 72.20278413290774, 162.7232117525041, 380.5948135560374, 680.411751668678, 94.41296191692246, 342.6301885212807, 0.9354514646021581, 1.0578644428162776] ],
    [ 1.733993279131329, [earth, venus, earth, venus, venus, earth, venus, venus], [7753.977222197127, 255.88107453329337, 75.5967416952974, 160.36036129893958, 382.1061268030645, 678.976863963736, 94.50715519472554, 343.6006980245842, 0.9256241681829921, 1.057832121612691] ],
    [ 1.774713574076225, [earth, venus, venus, venus, venus, earth, venus, venus], [8018.656979792823, 154.22278325981225, 427.70231716968834, 427.7171629352685, 427.74240786924787, 430.8186260638074, 109.6662090462626, 360.3642051241852, 0.9266133063265509, 1.0579076982277962] ],
    [ 1.774888928155373, [earth, venus, earth, earth, venus, venus, earth, venus], [7801.258708750266, 256.21351374982555, 251.82349960297893, 365.25605661326125, 133.79062188499515, 382.6793752060416, 668.5402743856215, 91.71362475669191, 1.8206053126432082, 28.81194230708524] ],
    [ 1.7805629578588085, [earth, venus, venus, earth, venus, venus, venus, earth, venus, venus], [7897.120952489119, 238.1201569042405, 399.5233831470826, 85.4578115146036, 375.0145138245868, 670.7965394080659, 670.7927721978574, 49.442931340982014, 418.97051286488414, 371.5231553046331, 2.2592940990253014, 1.057832121612691] ],
    [ 1.7805955873953385, [earth, earth, venus, venus, earth, venus, venus], [7909.982650355041, 686.7229772908232, 111.95481571990088, 433.9548614665072, 140.4674439102771, 151.18289787001052, 369.91042468842767, -4.037669929334977, 1.0578321216126905] ],
    [ 1.7856302320419277, [earth, venus, venus, earth, earth, venus, venus], [7336.206515484327, 213.1938194263948, 448.02903108701327, 60.3640015025876, 614.3233983544726, 110.16662403536526, 373.4151594822848, -4.053395184473299, 1.057834213231433] ],
    [ 1.8052698665604494, [earth, venus, earth, earth, venus, venus, earth, venus, venus], [7754.542673001531, 263.19849436694966, 169.55069465646395, 365.25558453567805, 205.32972011346772, 403.0087720615359, 52.313734077904336, 423.9583336316172, 364.64974697444785, -4.2258327314652835, 1.057832158548775] ],
    [ 1.8075209496061206, [earth, earth, venus, venus, earth, earth, venus, venus], [7336.1429021317745, 686.3932808950424, 114.86955817563523, 437.8874667881404, 64.62083600801546, 607.7679685241012, 108.9989080173761, 375.4573756980809, 0.9691206529677303, 1.05783212161269] ],
    [ 1.8118565098149784, [earth, venus, venus, earth, venus, venus, venus, earth, earth, venus], [7959.028680396746, 207.8294247650583, 407.4506923557096, 53.71285672883796, 625.5112556121242, 407.34463990530475, 674.1015602149877, 49.117882588411454, 564.1911705143149, 31.066903980781923, -4.1527240840965645, 1.057832121612691] ],
    [ 1.837723618951709, [earth, earth, earth, earth, earth, earth, venus], [7497.664221182352, 687.0855239670244, 687.1751671692465, 687.3316951220967, 687.4767150874649, 687.5248141106168, 108.93266673126028, 2.11324527025552, 1.057832121612691] ],
    [ 1.839167051848749, [earth, earth, earth, earth, earth, earth, earth, earth, venus], [7296.724239334399, 685.3444149860906, 685.190198686122, 685.0194030793318, 684.9270265843944, 684.9562911872705, 685.0944978299004, 685.2710597667663, 73.43733587241312, 0.9714180961919379, 1.0578490671978384] ],
    [ 1.864247761207542, [earth, earth, earth, venus, venus, earth, earth, venus, venus], [7225.836430831129, 685.7092493420422, 685.575337426275, 111.2892626508228, 449.3992661871816, 67.94602192421515, 615.7211040084571, 110.24635727192914, 380.70279679671, 1.055671860898033, 1.0659892850134913] ],
    [ 1.8658887531627575, [earth, earth, venus, venus, earth, venus, venus, venus, venus], [7938.056736711781, 666.628077582916, 106.09878929364706, 449.4002461984736, 62.505131189084054, 404.2791217115739, 674.0850051741737, 674.0850908654102, 410.89560639110823, 2.175328584308378, 1.05783768709899] ],
    [ 1.8729894320428704, [earth, venus, venus, earth, venus, venus, venus, venus, venus], [7309.955686504108, 242.00305306309562, 403.31913927172866, 80.568048104212, 376.3052464119222, 672.2642026142728, 672.2698205678452, 672.2914624962455, 410.3229994185495, 0.9756176647367582, 1.0578321217798627] ],
    [ 1.8735187725425484, [earth, venus, earth, earth, venus, venus, venus, venus, venus], [7788.561729659019, 238.65782832707453, 166.7078815622283, 365.255426818905, 196.15644082703054, 410.92792339517206, 674.0538897801287, 674.0549644133388, 410.89349675187555, -4.133467404073129, 1.05783212161269] ],
    [ 1.8755625640157687, [earth, venus, venus, earth, earth, venus, venus, venus, venus], [7901.360895449324, 235.9722606146112, 400.19274885800377, 83.04840312208357, 591.998005691323, 74.20029115660982, 674.0813799426254, 674.081256334343, 410.3421989142421, 0.9779600299878032, 1.0578332932285004] ],
    [ 1.8757581885216457, [earth, venus, venus, earth, earth, venus, venus, venus], [7911.238677211031, 229.6982216691547, 404.19322615318987, 78.08432408653192, 589.5653187763036, 72.6173223530331, 674.0957789489106, 409.98711202190236, 0.9818853857835502, 1.05783212161269] ],
    [ 1.8812570945817488, [earth, venus, venus, earth, venus, venus, venus], [7356.153471524599, 207.16928609132435, 427.8091273445595, 60.35472463920907, 370.1884503266965, 672.2525995378576, 410.358918545081, 1.0070220942190673, 1.057990197358877] ],
    [ 1.8866753034081278, [earth, venus, venus, venus, venus, venus, venus], [7905.37369692181, 228.82293545754675, 410.7008343211048, 671.967025733278, 671.9623159461596, 671.9613569671063, 410.80512982051357, 2.134085878461941, 1.057832121612691] ],
    [ 1.901715726905121, [earth, venus, venus, venus, venus, venus, venus, venus], [7365.44176105254, 211.94664730664866, 410.5689660809456, 673.1412277137839, 674.0652870399314, 673.1630466669125, 673.1679939111528, 410.4808484179143, 1.0574344224556145, 1.0747879697750988] ],
    [ 1.90856111660778, [earth, venus, venus, venus, venus, venus, venus, earth, venus], [7922.396938766176, 212.59178161282438, 427.05537821982296, 427.08506468427044, 427.10827103016834, 427.1161230111181, 427.10517252613135, 132.22114036406842, 159.59832201963212, -4.195691030284178, 21.97002779231867] ],
    [ 1.9129063818715633, [earth, venus, venus, venus, earth, venus, venus, earth, venus, venus], [7903.211077042927, 231.37553879160274, 407.63580087207646, 674.1011514180798, 657.8161373600847, 96.79397429150441, 355.1379748861882, 659.8329516442277, 58.520131065144355, 618.6998912028656, -4.173139107470366, 1.057832121612691] ],
    [ 1.9153864610433078, [earth, venus, earth, venus, venus, venus, venus, venus], [7757.269591064226, 246.2336990328128, 54.03289932516241, 397.3704583008034, 426.4657696845484, 426.43996516504114, 426.429100957594, 426.43594978845124, 0.8901482552542268, 1.05783212161269] ],
    [ 1.9187076228713216, [earth, earth, earth, venus, venus, earth, venus, venus], [7226.53234426167, 685.4063954577742, 685.2704139442257, 112.10967808983297, 449.39979288548795, 65.85131701208141, 393.14307031600725, 430.8054943175219, 2.3130458937972653, 1.057832121612691] ],
    [ 1.9216037772384567, [earth, earth, venus, venus, venus, venus, venus, venus, venus], [7365.979948054022, 664.5188206900091, 107.75871770423943, 427.7691560616607, 427.7969327829349, 427.8207083127001, 427.83256556177076, 427.82681736052143, 427.8058839381813, -4.266574124798483, 1.057832121612691] ],
    [ 1.9228892866489118, [earth, earth, earth, earth, earth, earth, venus, venus], [8083.247635462861, 686.8567541535681, 686.858196967787, 686.7375408343767, 686.5685987112794, 686.4457233458769, 112.7018039698527, 431.8578281966649, 2.2383701696767218, 1.05783212161269] ],
    [ 1.9433524956028476, [earth, venus, venus, venus, venus, venus, venus, venus, venus], [7821.55634222167, 256.634128754238, 440.92240457189337, 440.92330854003495, 440.92247025882494, 440.9189026698266, 440.91485171779567, 440.9098104822975, 440.90429806475015, -3.736334265127236, 1.057867526518909] ],
    [ 1.9442945793541364, [earth, earth, venus, venus, earth, earth, venus, venus, venus], [7377.946182632484, 656.2166898534144, 109.612685881796, 410.19890846764264, 72.80629265326039, 588.9327245019557, 76.16349432566007, 657.1594783265762, 657.1683032327055, 0.3696876823897329, 1.057832121612924] ],
    [ 1.9471185358614398, [earth, venus, venus, earth, venus, venus, earth, venus, venus, venus], [7360.801154787349, 227.1058337870481, 387.0853088322912, 55.81297758230131, 652.7568266813739, 369.64539440967854, 105.41372421750923, 409.1922269843929, 426.45214418857523, 426.43177163514184, -5.2317622347163155, 1.05783212161269] ],
    [ 1.9490886836187475, [earth, earth, earth, venus, venus, earth, venus, venus, venus], [7228.43149214068, 684.4563421650791, 684.3141529409088, 113.46383346915876, 449.4002499900998, 62.565133769927215, 404.34437702040054, 410.7966543033376, 673.5811591007862, -3.0067132628401607, 1.057832121612691] ],
    [ 1.9511665450089017, [earth, earth, earth, earth, venus, venus, venus, venus], [7690.662685044928, 688.0375985506248, 687.9641773353375, 687.8126305275346, 71.13631028247329, 446.92397580802117, 449.38316701305746, 446.9127239308262, -3.495198749253005, 1.05783212161269] ],
    [ 1.9515251740319741, [earth, earth, earth, venus, venus, venus, venus, venus, venus], [7215.971360108402, 689.8431079033692, 689.7401556588956, 111.27324079437459, 447.3607470422262, 447.3507285365856, 449.37732392771954, 447.32993367290146, 447.3238682611157, 2.829305084610254, 1.05783212161269] ],
    [ 1.9520216471935055, [earth, earth, earth, earth, venus, venus, venus, venus, venus], [7697.579862277622, 685.9208495161167, 685.8551355832512, 685.6927680891796, 70.70695805244155, 448.0288605662741, 449.34621263383247, 448.00814473355905, 447.9712096688045, -3.4345040588200475, 1.05783212161269] ],
    [ 1.9532840756119052, [earth, earth, venus, venus, venus, venus, venus, venus], [7939.252513946242, 664.0670264277566, 100.35383137938513, 448.78854651592553, 448.74693933347197, 448.9688692474528, 448.6753648441119, 448.657383409415, -3.1545656201715957, 1.057832121612691] ],
    [ 1.9569765232778245, [earth, earth, earth, earth, earth, venus, venus, venus], [8195.987394027512, 686.3826860939826, 686.5336984191499, 686.6939770577076, 686.7696509337255, 114.88191613000014, 448.45307400476474, 449.0155587722411, 5.820693871939833, 1.0578331510978916] ],
    [ 1.9665531411851553, [earth, earth, earth, earth, earth, earth, earth, venus], [7938.200705855204, 692.7896753134114, 692.7069338899953, 692.6949369439393, 692.7570521623732, 692.8722936842222, 692.9983666698088, 98.80676447085762, -4.069541078929321, 1.057832121612691] ],
    [ 1.9742649434924822, [earth, earth, venus, venus, earth, venus, venus, venus], [7377.0072854754, 657.2974459734044, 108.037016706972, 415.83769474910116, 71.63967641141917, 407.11063272820246, 660.1143934040823, 660.1274867659018, 6.104373271493067, 1.057832121612691] ],
    [ 2.031453659215179, [earth, venus, earth, venus, venus, venus, venus], [7755.6707947899695, 247.74703455228567, 54.754738838913525, 387.0329109331108, 437.6289084876073, 437.6212344277795, 437.6154244043581, 6.283185307179586, 1.057832121612691] ],
    [ 2.035968942008897, [earth, earth, venus, earth, earth, venus, venus, earth, venus], [7041.5179181581225, 730.5117429712125, 253.73904476290815, 168.25413838968112, 365.25543210311315, 196.419393361104, 410.49131779778384, 51.82872391531049, 348.41755932115825, 1.650441447093459, 9.38678249472233] ],
    [ 2.058308401955429, [earth, venus, venus, venus, venus, earth, venus, venus, venus], [7876.843342769882, 232.52423111093282, 432.08683385632736, 432.10172802885165, 432.1101414935594, 387.8659887573876, 81.40752718157002, 671.8630715210193, 410.8561237980522, 2.7335637831912654, 19.244826411431877] ],
    [ 2.087133245258814, [earth, earth, earth, earth, earth, venus, venus], [8203.136417376923, 684.7598038553859, 684.9122993119685, 685.0862099423026, 685.1729465148079, 114.7086434373021, 439.118058237921, -0.05145634021520329, 17.840080838799487] ],
    [ 2.088962246829354, [earth, earth, venus, venus, venus, venus, venus], [7359.087856555424, 667.8542514875644, 114.59927192407879, 410.7123408763878, 673.8949068171275, 673.8573678030606, 673.7229370097579, -0.207224818917385, 10.24472275495895] ],
    [ 2.103434369614721, [earth, venus, venus, venus, venus, venus, earth, venus, venus], [7757.854335234912, 247.84717932909373, 436.2677873811238, 436.2568671830304, 436.2477250688107, 436.2419847846781, 56.37733022273883, 385.5793102777996, 439.8227458900193, -1.229358804316074, 22.692391140122695] ],
    [ 2.1187279721014036, [earth, venus, earth, earth, earth, earth, earth, earth, venus], [7738.186731856183, 268.55317155877736, 74.2852574711633, 686.1572976897506, 686.1493039574613, 686.0178960153685, 685.8457933599993, 685.7296021318666, 99.0582188060496, -0.7745405740429184, 21.12319546344312] ],
    ]
    
def plot_solar_orbiter(index):
    
    fval, seq, pop_champion_x = results[index]

    # derived from https://github.com/esa/pykep/blob/49e35a8ff0e348d16abd9851938aeb8836a17277/doc/sphinx/examples/solar_orbiter.ipynb

    solar_orbiter = _solar_orbiter_udp([tmin, tmax], seq=seq)
    prob = pg.problem(pg.unconstrain(solar_orbiter,method="weighted",weights=[1.0, 10.0, 100, 100]))
    fval = prob.fitness(pop_champion_x) 
    print('sequence ' + names(seq))
    print('fval = ' + str(fval))
        
    solar_orbiter.pretty(pop_champion_x)
    solar_orbiter.plot(pop_champion_x)
    
    # Plot solar distance in AE
    timeframe = range(1,5*365)
    earth = jpl_lp("earth")
    venus = jpl_lp("venus")
    
    distances = []
    edistances = []
    vdistances = []
    
    for i in timeframe:
        epoch = pop_champion_x[0]+i
        pos, vel = solar_orbiter.eph(pop_champion_x, epoch)
        epos, evel = earth.eph(epoch)
        vpos, vvel = venus.eph(epoch)
        distances.append(norm(pos) / AU)
        edistances.append(norm(epos) / AU)
        vdistances.append(norm(vpos) / AU)
    
    fig, ax = plt.subplots()
    ax.plot(list(timeframe), distances, label="Solar Orbiter")
    ax.plot(list(timeframe), edistances, label="Earth")
    ax.plot(list(timeframe), vdistances, label="Venus")
    ax.set_xlabel("Days")
    ax.set_ylabel("AU")
    ax.set_title("Distance to Sun")
    ax.legend()
    
    # Plot inclination and distance
    inclinations = []
    for i in timeframe:
        epoch = pop_champion_x[0]+i
        pos, _ = solar_orbiter.eph(pop_champion_x, epoch)
        inclination = sign(pos[2])*acos(norm(pos[:2]) / norm(pos))
        inclinations.append(inclination)
    
    color = 'tab:red'
    fig2, ax2 = plt.subplots()
    ax2.plot(list(timeframe), inclinations, color=color)
    ax2.set_ylabel("Inclination", color=color)
    ax2.set_xlabel("Days")
    ax.set_title("Distance and Inclination")
    
    ax3 = ax2.twinx()  # instantiate a second axes that shares the same x-axis
    
    color = 'tab:blue'
    ax3.set_ylabel('AU', color=color)
    ax3.plot(list(timeframe), distances, color=color)
    ax3.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    
if __name__ == '__main__':
    plot_solar_orbiter(0)
    
    pass