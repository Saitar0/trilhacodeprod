import React from "react";
import { BlockType, ContentBlock, ProgressRecord, ProgressStatus } from "@/types";

export interface BlockProps {
  block: ContentBlock;
  type?: BlockType;
  isStaff?: boolean;
  trackId?: string;
  progress?: ProgressRecord;
  onProgress?: (status: ProgressStatus, data: Record<string, unknown>, attemptId?: string) => void;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
}
