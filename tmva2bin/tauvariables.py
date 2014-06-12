
LLH = [
    ("author","tau_author","I"),
    ("eta","tau_seedCalo_eta","F"),
    ("numTrack","tau_seedCalo_numTrack","I"),
    ("et","tau_Et","F"),
    ("nPi0","tau_nPi0","I"),
    ("NUM_PILEUP_AND_PRIMARY_VERTICES","tau_numberOfVertices","I"),
    ("dRmax","tau_calcVars_drMax","F"),
    ("centFrac","tau_seedCalo_centFrac","F"),
    ("calRadius","tau_calcVars_calRadius","F"),
    ("lead2ClusterEOverAllClusterE","tau_2leadClusterEOverTotalClusterE","F"),
    ("massTrkSys","tau_massTrkSys","F"),
    ("trFlightPathSig","tau_trFlightPathSig","F"),
    ("trkAvgDist","tau_seedCalo_trkAvgDist","F"),
    ("numWideTrack","tau_seedCalo_wideTrk_n","I")
]

TD2DPD = {
    "author"                : "tau_author",
    "numTrack"              : "tau_numTrack",
    "numWideTrack"          : "tau_seedCalo_wideTrk_n",
    "eta"                   : "tau_eta",
    "phi"                   : "tau_phi",
    "et"                    : "tau_Et",
    "pt"                    : "tau_pt",
    "charge"                : "tau_charge",
    "emRadius"              : "tau_seedCalo_EMRadius",
    "hadRadius"             : "tau_seedCalo_hadRadius",
    "isolFrac"              : "tau_seedCalo_isolFrac",
    "centFrac"              : "tau_seedCalo_centFrac",
    "stripWidth2"           : "tau_seedCalo_stripWidth2",
    "numStripCells"         : "tau_seedCalo_nStrip",
    "trFlightPathSig"       : "tau_trFlightPathSig",
    "ipSigLeadTrk"          : "tau_ipSigLeadTrk",
    "EToverpTLeadTrk"       : "tau_etOverPtLeadTrk",
    "z0SinThetaSig"         : "tau_ipZ0SinThetaSigLeadTrk",
    "massTrkSys"            : "tau_massTrkSys",
    "trkWidth2"             : "tau_trkWidth2",
    "nPi0"                  : "tau_nPi0",
    "nAssocTracksIsol"      : "tau_seedTrk_nIsolTrk",
    "trkAvgDist"            : "tau_seedCalo_trkAvgDist",
    "topoInvMass"           : "tau_topoInvMass",
    "effTopoInvMass"        : "tau_effTopoInvMass",
    "tau_effTopoInvMass"    : "tau_effTopoInvMass",
    "numTopoClusters"       : "tau_numTopoClusters",
    "numEffTopoClusters"    : "tau_numEffTopoClusters",
    "topoMeandR"            : "tau_topoMeanDeltaR",
    "effTopoMeandR"         : "tau_effTopoMeanDeltaR",
    "EMFractionCalib"       : "tau_calcVars_emFracCalib",
    "EMFractionAtEMScale"   : "tau_calcVars_EMFractionAtEMScale",
    "TRT_NHT_OVER_NLT"      : "tau_calcVars_TRTHTOverLT_LeadTrk",
    "numVertices"           : "vxp_n",
    "numGoodVertices"       : "evt_calcVars_numGoodVertices",
    "hadLeakEt"             : "tau_seedTrk_hadLeakEt",
    "secMaxStripEt"         : "tau_seedTrk_secMaxStripEt",
    "sumEMCellEtOverLeadTrkPt" : "tau_seedTrk_sumEMCellEtOverLeadTrkPt",
    "abs_eta"               : "tau_seedCalo_abs_eta",
    "BDT"                   : "BDT",
    "LLH"                   : "LLH",
    "tau_numberOfVertices"  : "tau_numberOfVertices",
    "tau_seedCalo_wideTrk_n": "tau_seedCalo_wideTrk_n",
    "tau_calcVars_calRadius": "tau_calcVars_calRadius",
    "CALRADIUS":              "tau_calcVars_calRadius",
    "tau_effClusterEOverTotalClusterE": "tau_effClusterEOverTotalClusterE",
    "tau_leadClusterEOverTotalClusterE": "tau_leadClusterEOverTotalClusterE",
    "tau_2leadClusterEOverTotalClusterE": "tau_2leadClusterEOverTotalClusterE",
    "tau_3leadClusterEOverTotalClusterE": "tau_3leadClusterEOverTotalClusterE",
    "tau_leadClusterLeadTrackdR": "tau_leadClusterLeadTrackdR",
    "tau_centFrac_cluster": "tau_centFrac_cluster",
    "tau_calcVars_drMax": "tau_calcVars_drMax",
    "DRMAX":            "tau_calcVars_drMax",
    "CALO_ISO_CORRECTED": "calo_iso_corrected",
    "NUM_PILEUP_AND_PRIMARY_VERTICES": "tau_numberOfVertices",
    "LEAD3CLUSTEREOVERALLCLUSTERE": "tau_3leadClusterEOverTotalClusterE",
    "ETHADFRAC": "tau_etHadFrac"
}

TD2DPD_caps = dict([(key.upper(),value) for key,value in TD2DPD.items()])
DPD2TD = dict([(value,key) for key,value in TD2DPD.items()])


def intersect(a, b):
     return list(set(a) & set(b))


def filter_variables(all_variables, variables_meta, prongs):
    filtered_variables = []
    for variable in all_variables:
        if variables_meta.has_key(variable):
            variable_meta = variables_meta[variable]
            if variable_meta.has_key('prongs'):
                if len(intersect(variable_meta["prongs"], prongs))==0:
                    continue
            filtered_variables.append(variable)
        else:
            print "variable %s was not found in metadata"% variable
            print "including it anyway"
            filtered_variables.append(variable)
    return filtered_variables
