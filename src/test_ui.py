from ui import GameUI, DummyShop

shop = DummyShop()
ui = GameUI(shop_client=shop, size=(900,640))
ui.run()
