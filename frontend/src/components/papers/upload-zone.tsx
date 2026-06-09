"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload } from "lucide-react";
import { uploadPapers } from "@/lib/api";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

export function UploadZone() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const qc = useQueryClient();

  const onDrop = useCallback(
    async (files: File[]) => {
      const pdfs = files.filter((f) => f.type === "application/pdf");
      if (!pdfs.length) {
        toast.error("Please upload PDF files only");
        return;
      }
      setUploading(true);
      try {
        await uploadPapers(pdfs, setProgress);
        toast.success(`Uploaded ${pdfs.length} paper(s). Processing started.`);
        qc.invalidateQueries({ queryKey: ["papers"] });
        qc.invalidateQueries({ queryKey: ["dashboard"] });
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Upload failed");
      } finally {
        setUploading(false);
        setProgress(0);
      }
    },
    [qc],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: true,
    disabled: uploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition-colors ${
        isDragActive ? "border-violet-500 bg-violet-500/10" : "border-zinc-700 bg-zinc-900/40 hover:border-zinc-600"
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto mb-4 h-10 w-10 text-violet-400" />
      <p className="text-lg font-medium text-zinc-200">
        {isDragActive ? "Drop PDFs here" : "Drag & drop research papers"}
      </p>
      <p className="mt-2 text-sm text-zinc-500">or click to browse — multiple files supported</p>
      {uploading && (
        <div className="mx-auto mt-6 max-w-xs">
          <div className="h-2 overflow-hidden rounded-full bg-zinc-800">
            <div className="h-full bg-violet-500 transition-all" style={{ width: `${progress}%` }} />
          </div>
          <p className="mt-2 text-xs text-zinc-500">{progress}%</p>
        </div>
      )}
    </div>
  );
}
