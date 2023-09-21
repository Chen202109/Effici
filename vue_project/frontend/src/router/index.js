import Vue from "vue";
import Router from "vue-router";

import LayoutComponent from '@/layout'

import WeekSaasWorksheetPage from '@/views/week_saas_worksheet/week_saas_worksheet';
import SaasUpgradeWorkPage from '@/views/week_saas_worksheet/saas_upgrade_work';

Vue.use(Router);

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
    {
        path: "/",
        redirect: "/login",
    },
    {
        path: "/login",
        name: "LoginPage",
        component: () => import("@/views/login/login"),
    },
    {
        path: "/user_management",
        component: LayoutComponent,
        children: [
            {
                path: "index",
                name: "UserManagementPage",
                component: () => import('@/views/user_management/user_management'),
            }
        ]
    },
    {
        path: "/week_saas_work_analysis",
        component: LayoutComponent,
        children: [
            {
                path: "index",
                name: "WeekSaasWorkAnalysisPage",
                component: () =>
                    import("@/views/week_saas_work_analysis/week_saas_work_analysis"),
            }
        ]
    },


    {
        path: "/saas_work_records",
        component: LayoutComponent,
        redirect: '/saas_work_records/week_saas_worksheet',
        children: [
            {
                path: "week_saas_worksheet",
                name: "WeekSaasWorksheetPage",
                component: WeekSaasWorksheetPage
            },
            {
                path: "saas_upgrade_work",
                name: "SaasUpgradeWorkPage",
                component: SaasUpgradeWorkPage
            }
        ]
    },
    {
        path: "/saas_worksheet_data_search",
        component: LayoutComponent,
        name: "SaasWorksheetDataSearch",
        redirect: '/saas_worksheet_data_search/saas_worksheet_data_search',
        children: [
            { 
                path: "saas_worksheet_data_search", 
                name: "SaasWorksheetDataSearchPage", 
                component: () =>
                    import("@/views/worksheet_data_search/saas_worksheet_data_search"),
            },
            { 
                path: "saas_upgrade_work_data_search", 
                name: "SaasUpgradeWorkDataSearch", 
                component: () =>
                    import("@/views/worksheet_data_search/saas_upgrade_work_data_search"),
            },
            { 
                path: "saas_license_data_search", 
                name: "SaasLicenseDataSearchPage", 
                component: () =>
                    import("@/views/worksheet_data_search/saas_license_data_search"),
            },
        ],
    },
];

const createRouter = () =>
    new Router({
        // mode: 'history', // require service support
        scrollBehavior: () => ({ y: 0 }),
        routes: constantRoutes,
    });

const router = createRouter();

// export function resetRouter() {
//     const newRouter = createRouter();
//     router.matcher = newRouter.matcher; // reset router
// }

export default router;
