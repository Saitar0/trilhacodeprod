import React from "react";
import { BlockType, ContentBlock, ProgressRecord, ProgressStatus } from "@/types";

export interface BlockProps {
  block: ContentBlock;
  type?: BlockType;
  progress?: ProgressRecord;
  onProgress?: (status: ProgressStatus, data: Record<string, unknown>) => void;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
  contentOverride?: React.ReactNode;
}
