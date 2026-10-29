<picture>
  <source media="(prefers-color-scheme: dark)" srcset="banner-dark.svg">
  <img alt="robert@derose ~ $ whoami: Robert DeRose, Nix, embedded Linux, device fleets, Apple containers" src="banner-light.svg">
</picture>

```
$ nix flake show github:RobertDeRose
github:RobertDeRose
├───fleet
│   ├───nixstasis       fleet monitoring + remote access, zero inbound ports
│   └───atomixos        NixOS for embedded devices
└───darwin
    ├───container-compose-plugin   docker compose for Apple container
    ├───container-runtime-krun     libkrun VM runtime for Apple container
    └───nix-hex-box                nix-darwin Linux builder on Apple containers
```

### Building

- [nixstasis](https://github.com/RobertDeRose/nixstasis): monitor and reach an IoT fleet with zero inbound ports on the devices. Elixir.
- [atomixos](https://github.com/RobertDeRose/atomixos): NixOS trimmed for embedded devices.
- [container-compose-plugin](https://github.com/RobertDeRose/container-compose-plugin): `docker compose` for Apple `container`. Swift.

### Experimental

- [container-runtime-krun](https://github.com/RobertDeRose/container-runtime-krun): swap in libkrun as Apple `container`'s VM runtime.
- [nix-hex-box](https://github.com/RobertDeRose/nix-hex-box): a nix-darwin Linux builder running on Apple containers.

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#363a4f','primaryTextColor':'#cad3f5','primaryBorderColor':'#8aadf4','lineColor':'#8087a2','clusterBkg':'#24273a','clusterBorder':'#494d64','titleColor':'#b8c0e0','edgeLabelBackground':'#1e2030','fontFamily':'ui-monospace, SFMono-Regular, Menlo, monospace'}}}%%
flowchart LR
  subgraph cfg["❄ how my machines are built"]
    direction TB
    nixcfg["<b>nix-config</b><br/>my Macs + Linux boxes"]
    maison["<b>maison</b><br/>the reusable framework"]
  end
  subgraph mac["▸ Apple container"]
    direction TB
    hex["<b>nix-hex-box</b><br/>Linux builder for Nix"]
    compose["<b>container-compose-plugin</b><br/>docker compose"]
    krun["<b>container-runtime-krun</b><br/>libkrun VM runtime"]
    tap["<b>homebrew-tap</b>"]
  end
  subgraph fleet["◉ devices in the field"]
    direction TB
    atomix["<b>atomixos</b><br/>NixOS for embedded"]
    stasis["<b>nixstasis</b><br/>fleet monitoring, no inbound ports"]
  end
  nixcfg -- flake input --> hex
  maison -- flake input --> hex
  nixcfg -. same stack .- maison
  tap -- brew install --> compose
  atomix -- flake input --> stasis
  hex -. can build Linux for .-> atomix

  classDef c fill:#363a4f,stroke:#c6a0f6,color:#cad3f5
  classDef m fill:#363a4f,stroke:#8aadf4,color:#cad3f5
  classDef f fill:#363a4f,stroke:#a6da95,color:#cad3f5
  classDef priv stroke-dasharray:5 4
  class nixcfg,maison c
  class hex,compose,krun,tap m
  class atomix,stasis f
  class nixcfg priv
```

### Recently shipped

<!-- releases:start -->
| Release | Date |
| --- | --- |
| [nixstasis v0.3.0](https://github.com/RobertDeRose/nixstasis/releases/tag/v0.3.0) | 2026-10-22 |
| [nix-hex-box v1.3.0](https://github.com/RobertDeRose/nix-hex-box/releases/tag/v1.3.0) | 2026-10-22 |
| [container-compose-plugin v0.3.0](https://github.com/RobertDeRose/container-compose-plugin/releases/tag/v0.3.0) | 2026-10-18 |
| [maison v0.2.0](https://github.com/RobertDeRose/maison/releases/tag/v0.2.0) | 2026-08-06 |
| [log_config_watcher v0.3.1](https://github.com/RobertDeRose/log_config_watcher/releases/tag/v0.3.1) | 2025-04-18 |
<!-- releases:end -->

<p align="center">
  <samp>
    <a href="https://robertderose.github.io">site</a> ·
    <a href="https://github.com/RobertDeRose?tab=repositories">projects</a> ·
    <a href="https://github.com/RobertDeRose/homebrew-tap">homebrew tap</a> ·
    <a href="https://www.linkedin.com/in/RobertDeRose">linkedin</a> ·
    <a href="https://gitlab.com/RobertDeRose">gitlab</a>
  </samp>
</p>
