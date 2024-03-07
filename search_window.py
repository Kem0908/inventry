import tkinter as tk
import pandas as pd
import tkinter.ttk as ttk


class SearchWindow(tk.Frame):
    def __init__(self, master=None, parent=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("600x450")
        self.master.title("検索ウインドウ")
        self.pack()
        self.set_data()
        self.create_widgets()

    def set_data(self):
        # データ設定
        pd_list = pd.read_csv("data_file/parent_child.csv")
        self.data = pd_list[["上位品目番号","下位品目番号"]]

        # 追加
        pd_inv = pd.read_csv("data_file/output_invent.csv")
        self.inv = pd_inv[["品番1","残数","棚番"]]
        pd_weld = pd.read_csv("data_file/re_welding_parts.csv")
        self.weld = pd_weld[["品番","棚番","残数"]]

        self.colname_list = ["列番号", "品目番号", "残数", "棚番"]  # 検索結果に表示させる列名
        # self.colname_list = ["品目番号", "残数", "棚番"]  # 検索結果に表示させる列名
        self.width_list = [20, 230, 230, 140]
        self.search_col = "検索キーワード"  # 検索キーワードの入力されている列名


    def create_widgets(self):

        # 追加
        style = ttk.Style()
        style.configure("Treeview", font=("",15))
        style.configure("Treeview.Heading", font=("",15,"bold"))

        self.pw_main = ttk.PanedWindow(self.master, orient="vertical")
        self.pw_main.pack(expand=True, fill=tk.BOTH, side="left")
        self.pw_top = ttk.PanedWindow(self.pw_main, orient="horizontal", height=25)
        self.pw_main.add(self.pw_top)

        # 追加
        # self.pw_centre = ttk.PanedWindow(self.pw_main, orient="horizontal")
        # self.pw_main.add(self.pw_centre)

        self.pw_bottom = ttk.PanedWindow(self.pw_main, orient="vertical")
        self.pw_main.add(self.pw_bottom)
        self.create_input_frame(self.pw_top)
        self.create_tree(self.pw_bottom)

        # 追加
        # self.create_centre(self.pw_centre)

    def create_input_frame(self, parent):
        fm_input = ttk.Frame(parent, )
        parent.add(fm_input)
        lbl_keyword = ttk.Label(fm_input, text="製品番号", width=7, font=10)
        lbl_keyword.grid(row=1, column=1, padx=3, pady=2)
        self.keyword = tk.StringVar()
        # ent_keyword = ttk.Entry(fm_input, justify="center", textvariable=self.keyword)
        ent_keyword = ttk.Entry(fm_input, justify="left", textvariable=self.keyword)
        ent_keyword.grid(row=1, column=2, padx=2, pady=2)
        ent_keyword.bind("<Return>", self.search)

        # 追加
        button = tk.Button(fm_input, text="検索", font=10)
        button.grid(row=1, column=3, padx=3, pady=2)

    def create_tree(self, parent):
        self.result_text1 = tk.StringVar()
        lbl_result1 = ttk.Label(parent, textvariable=self.result_text1)
        parent.add(lbl_result1)
        self.tree = ttk.Treeview(parent)

        # 追加
        self.result_text2 = tk.StringVar()
        lbl_result2 = ttk.Label(parent, textvariable=self.result_text2)
        parent.add(lbl_result2)
        # self.tree = ttk.Treeview(parent, yscrollcommand=lambda  *args: scrollbar.set(*args))
        # scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)

        self.tree["column"] = self.colname_list
        self.tree["show"] = "headings"
        self.tree.bind("<Double-1>", self.onDuble)
        # for i, (colname, width) in enumerate(zip(self.colname_list, self.width_list)):
        #     self.tree.heading(i, text=colname)
        #     self.tree.column(i, width=width)
        self.tree.heading(0, text="列番号")
        self.tree.heading(1, text="品目番号")
        self.tree.heading(2, text="棚番")
        self.tree.heading(3, text="在庫数")

        self.tree.column(0, width=30, anchor="center")
        self.tree.column(1, width=150, anchor="center")
        self.tree.column(2, width=220, anchor="nw")
        self.tree.column(3, width=60, anchor="ne")
        parent.add(self.tree)

    def search(self, event=None): # 検索ワードから一致するデータを抽出
        product_id = self.keyword.get()
        result = self.data.loc[self.data["上位品目番号"] == product_id]
        # result = self.data[self.data[self.search_col].str.contains(keyword, na=False)]
        # self.update_tree_by_search_result(result)

        # 追加
        all_parts = list(self.get_all_sub_parts(result))
        inv_all_parts = self.get_parts_information(all_parts)
        df_all = pd.DataFrame(inv_all_parts)
        self.update_tree_by_search_result(df_all)

    # 子部品検索
    def get_all_sub_parts(self, parent_list):
        all_parts = set()
        for i in range(parent_list.shape[0]):
            child_id = parent_list.iloc[i, 1]
            all_parts.add(child_id)
            child_df = self.data.loc[self.data["上位品目番号"] == child_id]
            if not child_df.empty:
                all_parts |= self.get_all_sub_parts(child_df)
        return all_parts

    # 既存の子部品在庫
    def get_parts_information(self, parts_list):
        invent_info = list()
        for part in parts_list:
            inv_parts_df = self.inv.loc[self.inv["品番1"] == part]
            # inv_parts_df = self.inv.loc[self.inv["品目番号5"] == part]
            weld_parts_df = self.weld.loc[self.weld["品番"] == part]
            if not inv_parts_df.empty:
                id = inv_parts_df.iloc[0,0]
                num = inv_parts_df.iloc[0,1]
                place = inv_parts_df.iloc[0,2]
                tag = "auto"
                invent_info.append([id, num, place, tag])
                # invent_info.append([id, num, place])
            elif not weld_parts_df.empty:
                id = weld_parts_df.iloc[0,0]
                num = weld_parts_df.iloc[0,2]
                place = weld_parts_df.iloc[0,1] + ":   [溶接自動手配棚]"
                tag = "weld"
                invent_info.append([id, num, place, tag])

        return invent_info

    def update_tree_by_search_result(self, result):
        self.tree.delete(*self.tree.get_children())
        self.result_text1.set(f"{self.keyword.get()}の部品在庫状況")
        self.result_text2.set(f"検索結果：{len(result)}")
        for _, row in result.iterrows():
            id = row[0]
            num = row[1]
            place = row[2]
            tag = row[3]
            if tag == "auto":
                color = "white"
            elif tag == "weld":
                color = "green"
            self.tree.insert("", "end", values=[_ + 1, id, place, num], tags=color)
            # self.tree.insert("", "end", values=[id, num, place], tags=color)

        self.tree.tag_configure("green", background="green")
        self.tree.tag_configure("white", background="white")

    def onDuble(self, event):
        for item in self.tree.selection():
            print(self.tree.item(item)["values"])


def main():
    root = tk.Tk()
    app = SearchWindow(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()

