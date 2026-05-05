# BREAKING POINTS FOUND & FIXES

## Breaking Point #1: Wrong Endpoint URLs in TANTRA Bridge
**Location**: `src/adapters/tantra_bridge.py`
**Issue**: Calling non-existent endpoints
- Line 189: `/generate` doesn't exist on Prompt Runner
- Line 197: `/creator-core/generate-blueprint` doesn't exist on Creator Core  
- Line 206: Sending wrong request format to BHIV Core

**Fix**: Update to correct endpoints based on actual API structure

## Breaking Point #2: Creator Core Port Mismatch
**Issue**: Creator Core runs on port 8000 but main.py runs on port 8001
**Impact**: TANTRA bridge cannot reach Creator Core at expected port

**Fix**: Creator Core IS main.py at port 8001, not a separate service

## Breaking Point #3: Missing Prompt Runner API Endpoint
**Issue**: Prompt Runner doesn't have `/generate` endpoint
**Expected**: `/generate` 
**Actual**: Need to check prompt-runner01/api.py

**Fix**: Update TANTRA bridge to use correct Prompt Runner endpoint

## Breaking Point #4: Integration Bridge Wrong Endpoints
**Location**: `integration_bridge.py`
**Issue**: Same endpoint issues as TANTRA bridge
- Line 127: `/generate` on Prompt Runner
- Line 134: `/creator-core/generate-blueprint` on Creator Core

**Fix**: Align with actual API structure

## Breaking Point #5: BHIV Core Request Format
**Issue**: TANTRA bridge sends module="ttg" or "ttv" but Core doesn't have these modules
**Available modules**: finance, education, creator, video
**Impact**: Core will reject TTG/TTV requests

**Fix**: Map TTG/TTV to "creator" module with product metadata

## Breaking Point #6: Unicode Encoding in Test Script
**Location**: `comprehensive_flow_test.py`
**Issue**: Windows console can't display emoji characters
**Impact**: Test script crashes on first print

**Fix**: Already fixed - replaced emojis with [PASS]/[FAIL]

## Breaking Point #7: Missing Artifact Chain in Core Response
**Issue**: Core response doesn't include execution_envelope by default
**Impact**: TANTRA bridge can't extract artifact chain

**Fix**: Core DOES include execution_envelope - need to verify extraction logic

## Breaking Point #8: Bucket Storage Endpoint
**Issue**: TANTRA bridge assumes bucket at port 8005
**Reality**: Bucket may not be running or may have different endpoint structure

**Fix**: Add fallback handling for bucket unavailability

## Breaking Point #9: Pipeline Timeout Issues
**Issue**: 30-second timeout for full pipeline may be insufficient
**Impact**: Long-running requests will fail mid-pipeline

**Fix**: Increase timeouts and add retry logic

## Breaking Point #10: No Error Recovery
**Issue**: If any pipeline step fails, entire request fails
**Impact**: No partial results, no graceful degradation

**Fix**: Add error recovery and partial result handling
