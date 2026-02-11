import { Layout, Steps, Typography } from "antd";
import { useState } from "react";
import { PreviewPage } from "./pages/PreviewPage";
import { UploadPage } from "./pages/UploadPage";
import type { PreviewPayload, TransformOptions } from "./services/api";

type AppState =
  | {
      step: "upload";
    }
  | {
      step: "preview";
      file: File;
      options: TransformOptions;
      preview: PreviewPayload;
    };

export function App() {
  const [state, setState] = useState<AppState>({ step: "upload" });

  return (
    <Layout style={{ minHeight: "100vh", padding: 24 }}>
      <Layout.Content style={{ maxWidth: 1200, margin: "0 auto", width: "100%" }}>
        <Typography.Title level={3}>Finance Screening Web</Typography.Title>
        <Steps
          current={state.step === "upload" ? 0 : 1}
          items={[{ title: "Upload & Mapping" }, { title: "Preview & Export" }]}
          style={{ marginBottom: 24 }}
        />

        {state.step === "upload" ? (
          <UploadPage
            onPreviewReady={({ file, options, preview }) => {
              setState({ step: "preview", file, options, preview });
            }}
          />
        ) : (
          <PreviewPage
            file={state.file}
            options={state.options}
            preview={state.preview}
            onBack={() => setState({ step: "upload" })}
          />
        )}
      </Layout.Content>
    </Layout>
  );
}
