/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
*  Copyright 2015 Adobe Systems Incorporated
*  All Rights Reserved.
*
* NOTICE:  All information contained herein is, and remains
* the property of Adobe Systems Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained
* herein are proprietary to Adobe Systems Incorporated and its
* suppliers and are protected by all applicable intellectual property laws,
* including trade secret and or copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe Systems Incorporated.
**************************************************************************/
import{floodgate as t}from"../floodgate.js";import{util as e}from"../util.js";import{setExperimentCodeForAnalytics as o,removeExperimentCodeForAnalytics as n}from"../../common/experimentUtils.js";import{checkUserLocaleEnabled as r,safeParseFeatureFlag as a}from"../gsuite/util.js";import{TOUCHPOINT_REGISTRY as i}from"./touchpoint-registry.js";import{CACHE_PURGE_SCHEME as c}from"../constant.js";const l=["treatmentFlag","surface","verb","translations","promotionSourcePrefix","promotionSourceSuffix"];export function createTouchpointInit(s){const f=i[s];if(!f)throw new Error(`Unknown touchpoint: ${s}`);return function(t,e){const o=l.find(t=>!e[t]);if(o)throw new Error(`Touchpoint "${t}" missing required field: ${o}`)}(s,f),async function(i){const l=[t.hasFlag(f.treatmentFlag,c.NO_CALL),t.hasFlag(f.controlFlag,c.NO_CALL)];f.fteFlag&&l.push(t.hasFlag(f.fteFlag,c.NO_CALL));const s=await Promise.all(l),u=s[0],p=s[1],m=!!f.fteFlag&&s[2];let g;g=u?a(f.treatmentFlag):p?a(f.controlFlag):{},function(t){return!t||void 0===t.enLocaleEnabled&&void 0===t.nonEnLocaleEnabled}(g)&&f.devConfig&&(g={...f.devConfig,...g});const d=r(g?.enLocaleEnabled,g?.nonEnLocaleEnabled),h=!!f.preferenceKey&&!e.isAcrobatTouchPointEnabled(f.preferenceKey),T=u&&d&&!h,F=p&&d&&!h;T?(n(f.controlCode),o(f.treatmentCode)):F?(n(f.treatmentCode),o(f.controlCode)):(n(f.treatmentCode),n(f.controlCode));const y=g?.fileTypes||f.fileTypeMetadataFlags||[],C=y.length>0?await async function(e,o){const n=[];let r={};const a=e.map(async e=>{const a=`dc-cv-${o}-${e}-metadata`;if(!await t.hasFlag(a,c.NO_CALL))return;const i=t.getFeatureMeta(a);if(!i)return;let l;try{l=JSON.parse(i)}catch(t){return}l?.selectors?.forEach(t=>n.push(t)),r={...r,...l?.types}});return await Promise.all(a),{selectors:n,fileExtToMimeTypeMap:r}}(y,f.surface):{};let b={};f.fteFlag&&m&&(b=a(f.fteFlag));const S=f.translations||{},x={};S.fteTitle&&(x.title=e.getTranslation(S.fteTitle)),S.fteDescription&&(x.description=e.getTranslation(S.fteDescription)),S.closeButton&&(x.button=e.getTranslation(S.closeButton));i({enabled:T,controlEnabled:F,metadata:C,touchpointConfig:g,touchPointText:S.touchPointText?e.getTranslation(S.touchPointText):"",fteTooltipStrings:x,enableFte:m&&d,fteConfig:b,verb:f.verb,surface:f.surface,promotionSourcePrefix:f.promotionSourcePrefix,promotionSourceSuffix:f.promotionSourceSuffix,fteStorageKey:f.fteStorageKey,fteType:f.fteType})}}