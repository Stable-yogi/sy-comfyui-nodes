# SY node test index

Every input option of every node is run by `sy_nodetest.py` (kept with the project tools). Each node has its own page with the inputs, how it was tested and every case.

Totals: **151** nodes, **1081** cases, **949** passed, **132** rejected (expected), **0** failed, **8** nodes skipped.

## Failures

No failing cases.

## All nodes

| Node | Class | Cases | Passed | Rejected | Failed | Notes |
|---|---|---|---|---|---|---|
| [ApplyMaskToImage SY](SYApplyMaskToImage.md) | SYApplyMaskToImage | 4 | 4 | 0 | 0 | ok |
| [Aspect Bucket SY](SYAspectBucket.md) | SYAspectBucket | 15 | 14 | 1 | 0 | ok |
| [Aspect From Size SY](SYAspectFromSize.md) | SYAspectFromSize | 7 | 7 | 0 | 0 | ok |
| [Assert SY](SYAssert.md) | SYAssert | 3 | 2 | 1 | 0 | ok |
| [Batch Concat SY](SYBatchConcat.md) | SYBatchConcat | 2 | 2 | 0 | 0 | ok |
| [Batch Info SY](SYBatchInfo.md) | SYBatchInfo | 1 | 1 | 0 | 0 | ok |
| [Batch Pick SY](SYBatchPick.md) | SYBatchPick | 5 | 5 | 0 | 0 | ok |
| [Batch Repeat SY](SYBatchRepeat.md) | SYBatchRepeat | 5 | 5 | 0 | 0 | ok |
| [Batch Size Calc SY](SYBatchSizeCalc.md) | SYBatchSizeCalc | 7 | 7 | 0 | 0 | ok |
| [Batch To List SY](SYBatchToList.md) | SYBatchToList | 1 | 1 | 0 | 0 | ok |
| [Bool Logic SY](SYBoolLogic.md) | SYBoolLogic | 6 | 6 | 0 | 0 | ok |
| [Bool Value SY](SYBoolValue.md) | SYBoolValue | 2 | 2 | 0 | 0 | ok |
| [CLIP Loader SY](SYCLIPLoader.md) | SYCLIPLoader | 0 | 0 | 0 | 0 | run by hand with a real clip_l file on the processor: it loaded in 6 s and gave a CLIP |
| [Caption Prefix Suffix SY](SYCaptionPrefixSuffix.md) | SYCaptionPrefixSuffix | 6 | 6 | 0 | 0 | ok |
| [Caption Review SY](SYCaptionReview.md) | SYCaptionReview | 12 | 9 | 3 | 0 | ok |
| [Caption Style Request SY](SYCaptionStyleRequest.md) | SYCaptionStyleRequest | 9 | 9 | 0 | 0 | ok |
| [Chat Prompt Builder SY](SYChatPromptBuilder.md) | SYChatPromptBuilder | 6 | 0 | 6 | 0 | ok |
| [Checkpoint Loader Info SY](SYCheckpointLoaderInfo.md) | SYCheckpointLoaderInfo | 0 | 0 | 0 | 0 | run by hand with a real 6.5 GB SDXL checkpoint on the processor: 162 s, gave the model, CLIP, VAE and the i... |
| [Checkpoint Name Filter SY](SYCheckpointNameFilter.md) | SYCheckpointNameFilter | 2 | 2 | 0 | 0 | ok |
| [Clamp Remap SY](SYClampRemap.md) | SYClampRemap | 15 | 14 | 1 | 0 | ok |
| [Colour Match SY](SYColourMatch.md) | SYColourMatch | 3 | 3 | 0 | 0 | ok |
| [Colour Swatch SY](SYColourSwatch.md) | SYColourSwatch | 2 | 1 | 1 | 0 | ok |
| [Compare Metrics SY](SYCompareMetrics.md) | SYCompareMetrics | 4 | 4 | 0 | 0 | ok |
| [Counter SY](SYCounter.md) | SYCounter | 12 | 10 | 2 | 0 | ok |
| [CropByMask SY](SYCropByMask.md) | SYCropByMask | 11 | 11 | 0 | 0 | ok |
| [Crop To Aspect SY](SYCropToAspect.md) | SYCropToAspect | 11 | 11 | 0 | 0 | ok |
| [Dataset Pair Check SY](SYDatasetPairCheck.md) | SYDatasetPairCheck | 5 | 5 | 0 | 0 | ok |
| [Empty Latent SY](SYEmptyLatent.md) | SYEmptyLatent | 10 | 10 | 0 | 0 | ok |
| [Filename Builder SY](SYFilenameBuilder.md) | SYFilenameBuilder | 8 | 7 | 1 | 0 | ok |
| [Film Grain SY](SYFilmGrain.md) | SYFilmGrain | 9 | 9 | 0 | 0 | ok |
| [Find Replace SY](SYFindReplace.md) | SYFindReplace | 6 | 6 | 0 | 0 | ok |
| [Flip Rotate SY](SYFlipRotate.md) | SYFlipRotate | 6 | 6 | 0 | 0 | ok |
| [Float Value SY](SYFloatValue.md) | SYFloatValue | 3 | 3 | 0 | 0 | ok |
| [Folder Image Count SY](SYFolderImageCount.md) | SYFolderImageCount | 3 | 3 | 0 | 0 | ok |
| [Frame Interpolate Blend SY](SYFrameInterpolateBlend.md) | SYFrameInterpolateBlend | 4 | 4 | 0 | 0 | ok |
| [Frame Range Info SY](SYFrameRangeInfo.md) | SYFrameRangeInfo | 8 | 4 | 4 | 0 | ok |
| [Frame Rate Convert SY](SYFrameRateConvert.md) | SYFrameRateConvert | 7 | 7 | 0 | 0 | ok |
| [Frame Select SY](SYFrameSelect.md) | SYFrameSelect | 8 | 4 | 4 | 0 | ok |
| [Free VRAM SY](SYFreeVRAM.md) | SYFreeVRAM | 2 | 2 | 0 | 0 | ok |
| [Gaussian Blur SY](SYGaussianBlur.md) | SYGaussianBlur | 4 | 4 | 0 | 0 | ok |
| [If Else Number SY](SYIfElseNumber.md) | SYIfElseNumber | 6 | 6 | 0 | 0 | ok |
| [If Else Text SY](SYIfElseText.md) | SYIfElseText | 4 | 4 | 0 | 0 | ok |
| [Image Batch Split Every N SY](SYImageBatchSplitEveryN.md) | SYImageBatchSplitEveryN | 6 | 4 | 2 | 0 | ok |
| [Image Blend SY](SYImageBlend.md) | SYImageBlend | 8 | 8 | 0 | 0 | ok |
| [Image Compare SY](SYImageCompare.md) | SYImageCompare | 7 | 7 | 0 | 0 | ok |
| [Image Grid SY](SYImageGrid.md) | SYImageGrid | 12 | 11 | 1 | 0 | ok |
| [Image Hash Duplicate Check SY](SYImageHashDuplicate.md) | SYImageHashDuplicate | 7 | 7 | 0 | 0 | ok |
| [Image Info SY](SYImageInfo.md) | SYImageInfo | 1 | 1 | 0 | 0 | ok |
| [Image Metadata Reader SY](SYImageMetadataReader.md) | SYImageMetadataReader | 2 | 0 | 2 | 0 | ok |
| [Image Resize SY](SYImageResize.md) | SYImageResize | 22 | 22 | 0 | 0 | ok |
| [Int Value SY](SYIntValue.md) | SYIntValue | 3 | 3 | 0 | 0 | ok |
| [JSON Field Get SY](SYJSONFieldGet.md) | SYJSONFieldGet | 3 | 2 | 1 | 0 | ok |
| [JSON Prompt Builder SY](SYJSONPromptBuilder.md) | SYJSONPromptBuilder | 6 | 5 | 1 | 0 | ok |
| [Labelled AB Grid SY](SYLabelledABGrid.md) | SYLabelledABGrid | 13 | 12 | 1 | 0 | ok |
| [Layout Box SY](SYLayoutBox.md) | SYLayoutBox | 21 | 21 | 0 | 0 | ok |
| [Layout Boxes Merge SY](SYLayoutBoxesMerge.md) | SYLayoutBoxesMerge | 5 | 0 | 5 | 0 | ok |
| [Layout Boxes Preview SY](SYLayoutBoxesPreview.md) | SYLayoutBoxesPreview | 12 | 0 | 12 | 0 | ok |
| [Layout JSON Check SY](SYLayoutJsonCheck.md) | SYLayoutJsonCheck | 9 | 9 | 0 | 0 | ok |
| [Levels Adjust SY](SYLevelsAdjust.md) | SYLevelsAdjust | 12 | 12 | 0 | 0 | ok |
| [List Folder Files SY](SYListFolderFiles.md) | SYListFolderFiles | 4 | 4 | 0 | 0 | ok |
| [List To Batch SY](SYListToBatch.md) | SYListToBatch | 2 | 2 | 0 | 0 | ok |
| [Load Image From Folder SY](SYLoadImageFromFolder.md) | SYLoadImageFromFolder | 5 | 5 | 0 | 0 | ok |
| [Load Image Mini SY](SYLoadImageMini.md) | SYLoadImageMini | 1 | 1 | 0 | 0 | ok |
| [Load Text SY](SYLoadText.md) | SYLoadText | 2 | 1 | 1 | 0 | ok |
| [Loader Name Picker SY](SYLoaderNamePicker.md) | SYLoaderNamePicker | 9 | 1 | 8 | 0 | ok |
| [Longest Side Scale SY](SYLongestSideScale.md) | SYLongestSideScale | 13 | 13 | 0 | 0 | ok |
| [Lora Loader Stack SY](SYLoraLoaderStack.md) | SYLoraLoaderStack | 0 | 0 | 0 | 0 | needs a real model and CLIP. Its text and number rules have unit tests; a run with real LoRA files is still... |
| [LoRA Stack Text SY](SYLoraStackText.md) | SYLoraStackText | 17 | 17 | 0 | 0 | ok |
| [LoRA Trigger Words SY](SYLoraTriggerWords.md) | SYLoraTriggerWords | 2 | 2 | 0 | 0 | ok |
| [MaskCombine SY](SYMaskCombine.md) | SYMaskCombine | 4 | 4 | 0 | 0 | ok |
| [MaskFeather SY](SYMaskFeather.md) | SYMaskFeather | 4 | 4 | 0 | 0 | ok |
| [MaskFromBox SY](SYMaskFromBox.md) | SYMaskFromBox | 17 | 17 | 0 | 0 | ok |
| [MaskFromColour SY](SYMaskFromColour.md) | SYMaskFromColour | 10 | 10 | 0 | 0 | ok |
| [MaskGrowShrink SY](SYMaskGrowShrink.md) | SYMaskGrowShrink | 5 | 5 | 0 | 0 | ok |
| [MaskInvertThreshold SY](SYMaskInvertThreshold.md) | SYMaskInvertThreshold | 5 | 5 | 0 | 0 | ok |
| [MaskOverlayPreview SY](SYMaskOverlayPreview.md) | SYMaskOverlayPreview | 9 | 9 | 0 | 0 | ok |
| [MaskToBox SY](SYMaskToBox.md) | SYMaskToBox | 7 | 7 | 0 | 0 | ok |
| [Math Expression SY](SYMathExpression.md) | SYMathExpression | 8 | 7 | 1 | 0 | ok |
| [Megapixel Scale SY](SYMegapixelScale.md) | SYMegapixelScale | 13 | 13 | 0 | 0 | ok |
| [Min Max SY](SYMinMax.md) | SYMinMax | 5 | 5 | 0 | 0 | ok |
| [Model Preset Bundle SY](SYModelPresetBundle.md) | SYModelPresetBundle | 14 | 14 | 0 | 0 | ok |
| [Multiline Text SY](SYMultilineText.md) | SYMultilineText | 3 | 3 | 0 | 0 | ok |
| [Negative Prompt Presets SY](SYNegativePromptPresets.md) | SYNegativePromptPresets | 12 | 11 | 1 | 0 | ok |
| [Note SY](SYNote.md) | SYNote | 6 | 6 | 0 | 0 | ok |
| [Number Compare SY](SYNumberCompare.md) | SYNumberCompare | 10 | 10 | 0 | 0 | ok |
| [Orientation SY](SYOrientation.md) | SYOrientation | 3 | 3 | 0 | 0 | ok |
| [Pad Image SY](SYPadImage.md) | SYPadImage | 15 | 15 | 0 | 0 | ok |
| [Paint Mask SY](SYPaintMask.md) | SYPaintMask | 0 | 0 | 0 | 0 | tested in a real ComfyUI page: painted, ran the workflow, saved and reloaded it, and the mask came back unc... |
| [PasteBack SY](SYPasteBack.md) | SYPasteBack | 5 | 4 | 1 | 0 | ok |
| [Ping Pong SY](SYPingPong.md) | SYPingPong | 2 | 2 | 0 | 0 | ok |
| [Pixel Count Info SY](SYPixelCountInfo.md) | SYPixelCountInfo | 7 | 7 | 0 | 0 | ok |
| [Precision Info SY](SYPrecisionInfo.md) | SYPrecisionInfo | 17 | 17 | 0 | 0 | ok |
| [Prompt Choice SY](SYPromptChoice.md) | SYPromptChoice | 4 | 4 | 0 | 0 | ok |
| [Prompt Cleaner SY](SYPromptCleaner.md) | SYPromptCleaner | 3 | 3 | 0 | 0 | ok |
| [Prompt Enhance Request SY](SYPromptEnhanceRequest.md) | SYPromptEnhanceRequest | 12 | 0 | 12 | 0 | ok |
| [Prompt Style Templates SY](SYPromptStyleTemplates.md) | SYPromptStyleTemplates | 15 | 15 | 0 | 0 | ok |
| [Prompt Weight Wrap SY](SYPromptWeightWrap.md) | SYPromptWeightWrap | 9 | 9 | 0 | 0 | ok |
| [Random Choice SY](SYRandomChoice.md) | SYRandomChoice | 4 | 0 | 4 | 0 | ok |
| [Random In Range SY](SYRandomInRange.md) | SYRandomInRange | 8 | 6 | 2 | 0 | ok |
| [Regex Extract SY](SYRegexExtract.md) | SYRegexExtract | 8 | 5 | 3 | 0 | ok |
| [Resolution SY](SYResolution.md) | SYResolution | 19 | 19 | 0 | 0 | ok |
| [Reverse Batch SY](SYReverseBatch.md) | SYReverseBatch | 1 | 1 | 0 | 0 | ok |
| [Round To Multiple SY](SYRoundToMultiple.md) | SYRoundToMultiple | 9 | 9 | 0 | 0 | ok |
| [Run Timer SY](SYRunTimer.md) | SYRunTimer | 2 | 2 | 0 | 0 | ok |
| [Safetensors Header Info SY](SYSafetensorsHeaderInfo.md) | SYSafetensorsHeaderInfo | 3 | 3 | 0 | 0 | ok |
| [Sampler Settings SY](SYSamplerSettings.md) | SYSamplerSettings | 23 | 23 | 0 | 0 | ok |
| [Sampler Settings Unpack SY](SYSamplerSettingsUnpack.md) | SYSamplerSettingsUnpack | 0 | 0 | 0 | 0 | needs the settings object from Sampler Settings SY. Its unit test checks the unpacking; a run inside a full... |
| [Save Image To Folder SY](SYSaveImageToFolder.md) | SYSaveImageToFolder | 11 | 10 | 1 | 0 | ok |
| [Save Text SY](SYSaveText.md) | SYSaveText | 7 | 5 | 2 | 0 | ok |
| [Save With Caption SY](SYSaveWithCaption.md) | SYSaveWithCaption | 11 | 0 | 11 | 0 | ok |
| [3D Scene SY](SYScene3D.md) | SYScene3D | 0 | 0 | 0 | 0 | tested in a real ComfyUI page: added shapes, turned the camera, loaded a .glb cube, saved and reloaded the ... |
| [Seed SY](SYSeed.md) | SYSeed | 5 | 5 | 0 | 0 | ok |
| [Seed List SY](SYSeedList.md) | SYSeedList | 7 | 7 | 0 | 0 | ok |
| [Seed Stepper SY](SYSeedStepper.md) | SYSeedStepper | 12 | 12 | 0 | 0 | ok |
| [Select By Index Text SY](SYSelectByIndexText.md) | SYSelectByIndexText | 12 | 12 | 0 | 0 | ok |
| [Sharpen SY](SYSharpen.md) | SYSharpen | 7 | 7 | 0 | 0 | ok |
| [Short ID SY](SYShortID.md) | SYShortID | 10 | 10 | 0 | 0 | ok |
| [Show Text SY](SYShowText.md) | SYShowText | 1 | 1 | 0 | 0 | ok |
| [Size Presets SY](SYSizePresets.md) | SYSizePresets | 20 | 20 | 0 | 0 | ok |
| [Size Snap SY](SYSizeSnap.md) | SYSizeSnap | 12 | 12 | 0 | 0 | ok |
| [Crop Square Centre For Training SY](SYSquareCropTrain.md) | SYSquareCropTrain | 7 | 7 | 0 | 0 | ok |
| [Swap Width Height SY](SYSwapWidthHeight.md) | SYSwapWidthHeight | 8 | 8 | 0 | 0 | ok |
| [Switch SY](SYSwitch.md) | SYSwitch | 2 | 2 | 0 | 0 | ok |
| [System Info SY](SYSystemInfo.md) | SYSystemInfo | 1 | 1 | 0 | 0 | ok |
| [System Prompt Presets SY](SYSystemPromptPresets.md) | SYSystemPromptPresets | 13 | 13 | 0 | 0 | ok |
| [Tag Frequency SY](SYTagFrequency.md) | SYTagFrequency | 8 | 6 | 2 | 0 | ok |
| [Text SY](SYText.md) | SYText | 3 | 3 | 0 | 0 | ok |
| [Text Case Trim SY](SYTextCaseTrim.md) | SYTextCaseTrim | 9 | 9 | 0 | 0 | ok |
| [Text Chunker SY](SYTextChunker.md) | SYTextChunker | 10 | 0 | 10 | 0 | ok |
| [Text Contains SY](SYTextContains.md) | SYTextContains | 4 | 0 | 4 | 0 | ok |
| [Text Join SY](SYTextJoin.md) | SYTextJoin | 7 | 7 | 0 | 0 | ok |
| [Text Number Format SY](SYTextNumberFormat.md) | SYTextNumberFormat | 10 | 10 | 0 | 0 | ok |
| [Text Split Lines SY](SYTextSplitLines.md) | SYTextSplitLines | 6 | 0 | 6 | 0 | ok |
| [Text Stats SY](SYTextStats.md) | SYTextStats | 2 | 2 | 0 | 0 | ok |
| [Text Template SY](SYTextTemplate.md) | SYTextTemplate | 10 | 8 | 2 | 0 | ok |
| [Text Trim To Tokens SY](SYTextTrimToTokens.md) | SYTextTrimToTokens | 7 | 7 | 0 | 0 | ok |
| [Tile Grid Calc SY](SYTileGridCalc.md) | SYTileGridCalc | 13 | 10 | 3 | 0 | ok |
| [Timestamp SY](SYTimestamp.md) | SYTimestamp | 6 | 6 | 0 | 0 | ok |
| [Token Estimate SY](SYTokenEstimate.md) | SYTokenEstimate | 2 | 2 | 0 | 0 | ok |
| [Unet Loader SY](SYUnetLoader.md) | SYUnetLoader | 0 | 0 | 0 | 0 | run by hand with a real unet file on the processor: it loaded in 6 s and gave a model |
| [VAE Loader SY](SYVAELoader.md) | SYVAELoader | 0 | 0 | 0 | 0 | run by hand with a real 160 MB VAE file on the processor: it loaded in 14 s and gave a VAE |
| [Video Frame Counter SY](SYVideoFrameCounter.md) | SYVideoFrameCounter | 12 | 12 | 0 | 0 | ok |
| [Video Frames Calc SY](SYVideoFramesCalc.md) | SYVideoFramesCalc | 8 | 7 | 1 | 0 | ok |
| [Video Loop Frames SY](SYVideoLoopFrames.md) | SYVideoLoopFrames | 5 | 5 | 0 | 0 | ok |
| [Video Size Presets SY](SYVideoSizePresets.md) | SYVideoSizePresets | 6 | 6 | 0 | 0 | ok |
| [Vignette SY](SYVignette.md) | SYVignette | 6 | 6 | 0 | 0 | ok |
| [VRAM Estimate SY](SYVramEstimate.md) | SYVramEstimate | 7 | 7 | 0 | 0 | ok |
| [XY Grid Assemble SY](SYXYGridAssemble.md) | SYXYGridAssemble | 13 | 12 | 1 | 0 | ok |
| [XY Label Strip SY](SYXYLabelStrip.md) | SYXYLabelStrip | 5 | 0 | 5 | 0 | ok |
| [XY Pick SY](SYXYPick.md) | SYXYPick | 6 | 4 | 2 | 0 | ok |
| [XY Values List SY](SYXYValuesList.md) | SYXYValuesList | 21 | 21 | 0 | 0 | ok |
