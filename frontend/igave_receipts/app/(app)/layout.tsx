import DashboardLayout from "../components/DashboardLayout";
import DashboardNav from "../components/DashboardNav";




export default function AppGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardLayout>
      <DashboardNav />
      {children}
    </DashboardLayout>
  );
}
