import { Atom ,CodeXml , Home, Inbox, Search, Settings, BookOpen, CircleEllipsis  } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

// Menu items.
const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  }, 
  {
    title: "GroundState",
    url: "/groundstate",
    icon: Atom ,
  },
  {
    title: "PlayGround",
    url: "/playground",
    icon: Inbox,
  },
  {
    title: "Search",
    url: "/search",
    icon: Search,
  },
  {
    title: "API",
    url: "http://localhost:8000/docs",
    icon: CodeXml ,
  },
  {
    title : "Docs",
    url : "/docs",
    icon : BookOpen
  },
  {
    title: "Settings",
    url: "/setting",
    icon: Settings
  },
  {
    title: "More",
    url: "/more",
    icon: CircleEllipsis 
  },
]

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup className="bg-stone-200 h-full">
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}