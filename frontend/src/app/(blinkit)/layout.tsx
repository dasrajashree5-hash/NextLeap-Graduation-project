import BlinkitApp from "@/components/BlinkitApp";

export default function BlinkitLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <BlinkitApp />
      {children}
    </>
  );
}
