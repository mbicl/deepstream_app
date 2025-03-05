/*
Custom bbox parser for YUNET onnx model
Author: Maqsud Baxriddinov
Date: 05-03-2025
*/

#include "nvdsinfer_custom_impl.h"
#include <cmath>
#include <cstring>
#include <iostream>
#include <vector>

#define CONF_THRESH 0.5 // Minimum confidence threshold

static const char *CLS_OUTPUTS[] = {"cls_8", "cls_16", "cls_32"};
static const char *OBJ_OUTPUTS[] = {"obj_8", "obj_16", "obj_32"};
static const char *BBOX_OUTPUTS[] = {"bbox_8", "bbox_16", "bbox_32"};
static const char *KPS_OUTPUTS[] = {"kps_8", "kps_16", "kps_32"};

extern "C" bool NvDsInferParseCustomYUNet(
	std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
	NvDsInferNetworkInfo const &networkInfo,
	NvDsInferParseDetectionParams const &detectionParams,
	std::vector<NvDsInferObjectDetectionInfo> &objectList) {

	std::vector<int> strides = {8, 16, 32};
	for (int i = 0; i < strides.size(); ++i) {
		const float *cls_scores = nullptr;
		const float *obj_scores = nullptr;
		const float *bboxes = nullptr;
		const float *keypoints = nullptr;
		int num_priors = 0;

		for (const auto &layer : outputLayersInfo) {			
			if (strcmp(layer.layerName, CLS_OUTPUTS[scale]) == 0) {
				cls_scores = static_cast<const float *>(layer.buffer);
				num_priors = layer.inferDims.d[1];
			} else if (strcmp(layer.layerName, OBJ_OUTPUTS[scale]) == 0) {
				obj_scores = static_cast<const float *>(layer.buffer);
			} else if (strcmp(layer.layerName, BBOX_OUTPUTS[scale]) == 0) {
				bboxes = static_cast<const float *>(layer.buffer);
			} else if (strcmp(layer.layerName, KPS_OUTPUTS[scale]) == 0) {
				keypoints = static_cast<const float *>(layer.buffer);
			}
		}

		if (!cls_scores || !obj_scores || !bboxes) {
			std::cerr << "[ERROR] Missing output buffers for scale " << (1 << (scale + 3)) << "x." << std::endl;
			continue;
		}

		for (int i = 0; i < num_priors; ++i) {
			float confidence = cls_scores[i] * obj_scores[i];
			if (confidence < CONF_THRESH) continue;

			NvDsInferObjectDetectionInfo obj;
			obj.classId = 0; // Face class
			obj.detectionConfidence = confidence;

			obj.left = std::max(0.0f, std::min(obj.left, (float)networkInfo.width - 1));
			obj.top = std::max(0.0f, std::min(obj.top, (float)networkInfo.height - 1));
			obj.width = std::max(1.0f, std::min(obj.width, (float)networkInfo.width));
			obj.height = std::max(1.0f, std::min(obj.height, (float)networkInfo.height));

			objectList.push_back(obj);
		}
	}

	return true;
}

CHECK_CUSTOM_PARSE_FUNC_PROTOTYPE(NvDsInferParseCustomYUNet);